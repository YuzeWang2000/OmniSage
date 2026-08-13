"""Bound blocking RAG work so it cannot exhaust Starlette's shared thread pool."""

from anyio import CapacityLimiter, to_thread

from ..config import settings


_rag_limiter = CapacityLimiter(settings.RAG_WORKER_LIMIT)


async def run_rag_work(function, *args):
    return await to_thread.run_sync(function, *args, limiter=_rag_limiter)
