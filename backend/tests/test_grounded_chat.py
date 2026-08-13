from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.ai.contracts.messages import NormalizedMessage, TextPart
from app.ai.contracts.requests import NormalizedChatRequest, RetrievalOptions, WorkflowType
from app.ai.errors import KnowledgeBaseNotFoundError
from app.ai.workflows.grounded_chat import augment_with_local_retrieval


def test_grounded_chat_passes_query_and_local_model_in_correct_order(monkeypatch):
    request = NormalizedChatRequest(
        conversation_id=1,
        model_key="deepseek::connection::model",
        workflow=WorkflowType.GROUNDED_CHAT,
        messages=[NormalizedMessage(role="user", content=[TextPart(text="question")])],
        retrieval=RetrievalOptions(enabled=True, knowledge_base_id=3, top_k=7, score_threshold=0.4),
    )
    kb = SimpleNamespace(vector_db_path="vectors", embedding_model="local-embedding")
    monkeypatch.setattr(
        "app.services.database_service.DatabaseService.get_knowledge_base_by_id",
        lambda *_: kb,
    )
    observed = {}

    def fake_search(query, vector_db_path, embedding_model, top_k, min_score):
        observed.update(
            query=query,
            vector_db_path=vector_db_path,
            embedding_model=embedding_model,
            top_k=top_k,
            min_score=min_score,
        )
        return {"threshold": 0.4, "results": [{"content": "grounding evidence"}]}

    monkeypatch.setattr(
        "app.ai.workflows.grounded_chat.knowledge_base_service.search_knowledge_base",
        fake_search,
    )
    result = augment_with_local_retrieval(request, user_id=9, db=object())
    assert observed == {
        "query": "question",
        "vector_db_path": "vectors",
        "embedding_model": "local-embedding",
        "top_k": 7,
        "min_score": 0.4,
    }
    assert "grounding evidence" in result.messages[0].text()
    assert request.messages[0].text() == "question"


def test_grounded_chat_requires_a_knowledge_base_unless_wiki_is_enabled():
    with pytest.raises(ValidationError):
        NormalizedChatRequest(
            conversation_id=1,
            model_key="deepseek::connection::model",
            workflow=WorkflowType.GROUNDED_CHAT,
            messages=[NormalizedMessage(role="user", content=[TextPart(text="question")])],
            retrieval=RetrievalOptions(enabled=True),
        )
    request = NormalizedChatRequest(
        conversation_id=1,
        model_key="deepseek::connection::model",
        workflow=WorkflowType.GROUNDED_CHAT,
        messages=[NormalizedMessage(role="user", content=[TextPart(text="question")])],
        retrieval=RetrievalOptions(enabled=True, wiki=True),
    )
    assert request.retrieval.wiki is True


def test_missing_owned_knowledge_base_is_a_standard_not_found_error(monkeypatch):
    request = NormalizedChatRequest(
        conversation_id=1,
        model_key="deepseek::connection::model",
        workflow=WorkflowType.GROUNDED_CHAT,
        messages=[NormalizedMessage(role="user", content=[TextPart(text="question")])],
        retrieval=RetrievalOptions(enabled=True, knowledge_base_id=999),
    )
    monkeypatch.setattr(
        "app.services.database_service.DatabaseService.get_knowledge_base_by_id",
        lambda *_: None,
    )
    with pytest.raises(KnowledgeBaseNotFoundError):
        augment_with_local_retrieval(request, user_id=9, db=object())
