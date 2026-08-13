from ...services.knowledgebase_service import knowledge_base_service
from ..contracts.messages import NormalizedMessage, TextPart
from ..errors import InvalidRetrievalConfigError, KnowledgeBaseNotFoundError, UnsupportedTaskError


class LocalEmbeddingModelHandle:
    """Boundary around the existing Ollama embedding implementation."""


class LocalRerankModelHandle:
    """Boundary around the existing local reranker implementation."""


def augment_with_local_retrieval(request, user_id: int, db):
    if not request.retrieval.enabled:
        return request
    question = request.messages[-1].text()
    if request.retrieval.wiki:
        wiki = knowledge_base_service.rag_chain_service.get_wiki_knowledge_base()
        if not wiki:
            raise UnsupportedTaskError("Wiki retrieval is unavailable")
        documents = wiki.wiki_service.search(question, max_results=request.retrieval.top_k)
        context = "\n\n".join(str(item.get("content", "")) for item in documents)
    else:
        kb_id = request.retrieval.knowledge_base_id
        if kb_id is None:
            raise InvalidRetrievalConfigError("knowledge_base_id is required for grounded_chat")
        from ...services.database_service import DatabaseService
        kb = DatabaseService.get_knowledge_base_by_id(kb_id, user_id, db)
        if not kb:
            raise KnowledgeBaseNotFoundError("knowledge base not found or access denied")
        documents = knowledge_base_service.search_knowledge_base(
            question, kb.vector_db_path, kb.embedding_model,
            top_k=request.retrieval.top_k, min_score=request.retrieval.score_threshold,
        )
        context = "\n\n".join(
            item.get("content", "") for item in documents.get("results", [])
        )
    if not context:
        context = "未检索到相关资料。请明确说明资料不足。"
    copy = request.model_copy(deep=True)
    copy.messages.insert(0, NormalizedMessage(role="system", content=[TextPart(text=f"仅根据以下检索资料回答；资料不足时明确说明。\n\n{context}")]))
    return copy
