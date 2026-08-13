import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from .. import schemas
from ..ai.errors import AIError
from ..ai.providers import register_builtin_providers
from ..ai.services import connection_service, model_catalog_service
from ..ai.workflows import validate_chat
from ..ai.workflows.grounded_chat import augment_with_local_retrieval
from ..database import SessionLocal
from ..security import AuthenticatedUser, get_current_user
from ..services.database_service import DatabaseService
from ..services.blocking_work import run_rag_work

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()


@router.post("/stream")
async def chat_stream_endpoint(req: schemas.ChatRequest, db: Session = Depends(get_db), current_user: AuthenticatedUser = Depends(get_current_user)):
    conversation = DatabaseService.get_conversation_by_id(req.conversation_id, current_user.id, db)
    if not conversation: raise HTTPException(status_code=404, detail="对话不存在或无权访问")
    model = model_catalog_service.get_model(db, current_user.id, req.model_key)
    connection = connection_service.require_active(
        connection_service.get_owned(db, current_user.id, model.connection_id)
    )
    # Streaming starts after the request handler returns. Never carry an ORM
    # instance or the request-scoped Session into that asynchronous lifetime.
    runtime_connection = connection_service.runtime_snapshot(connection)
    provider_credential = connection_service.credential(connection)
    validate_chat(model, req)
    provider = register_builtin_providers().get(connection.provider)
    incoming_messages = list(req.messages)
    provider_req = req.model_copy(update={
        "messages": DatabaseService.build_chat_context(
            req.conversation_id, incoming_messages, req.regenerate, db,
        )
    })
    if req.workflow.value == "grounded_chat":
        def retrieve_context():
            # Embedding and Chroma are blocking. Keep them out of the async SSE
            # handler and give retrieval its own short-lived database session.
            with SessionLocal() as retrieval_db:
                return augment_with_local_retrieval(provider_req, current_user.id, retrieval_db)
        provider_req = await run_rag_work(retrieve_context)
    if not DatabaseService.get_chat_history(req.conversation_id, db) and conversation.title == "新对话":
        DatabaseService.update_conversation_title(req.conversation_id, current_user.id, req.messages[-1].text()[:10] or "新对话", db)

    async def generate():
        answer = ""
        try:
            async for event in provider.stream_chat(runtime_connection, model, provider_req, provider_credential):
                if event.type == "content_delta" and event.content: answer += event.content
                if event.type == "done":
                    continue
                yield f"data: {event.model_dump_json(exclude_none=True)}\n\n"
            with SessionLocal() as stream_db:
                saved = (DatabaseService.replace_latest_chat_response(req.conversation_id, incoming_messages, answer, req.model_key, stream_db)
                    if req.regenerate else DatabaseService.save_chat_history(req.conversation_id, incoming_messages, answer, req.model_key, stream_db))
            if not saved: raise RuntimeError("message persistence failed")
            yield f"data: {json.dumps({'type':'done'})}\n\n"
        except GeneratorExit:
            raise
        except AIError as exc:
            yield f"data: {json.dumps({'type':'error','code':exc.code,'message':str(exc)})}\n\n"
        except Exception:
            logger.exception("chat stream failed")
            yield f"data: {json.dumps({'type':'error','code':'ProviderUnavailable','message':'回答生成失败，请稍后重试'})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream", headers={"Cache-Control":"no-cache, no-transform", "X-Accel-Buffering":"no"})
