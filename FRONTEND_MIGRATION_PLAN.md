# React 与 AI Provider 迁移结果

React 客户端已接管 `frontend/`；`frontend-legacy/` 仅供历史参考，不是默认入口、不兼容新 Provider 架构、不保证运行，也不应作为新功能开发基础。

迁移后的事实来源是 FastAPI `openapi.json`。模型与凭证功能已由旧 `/models` 和 `/api-keys/*` 迁移到 `/ai/providers`、`/ai/connections`、`/ai/models`；聊天已迁移为 connection-scoped model key、ContentPart、workflow/options/retrieval 和 type-based SSE。前端连接/模型目录用 TanStack Query，Zustand 只保存未提交 UI 偏好。

保留功能：JWT 认证、会话 CRUD、标准流式聊天、知识库上传/检索、Wiki、grounded chat、本地 Embedding/Reranker、响应式与无障碍交互。未迁移为实际能力：旧 Vosk 语音输入；新架构也尚未实现媒体 Asset、在线 Embedding/Rerank、TTS/STT 或视觉调用。

破坏性数据库策略、丢失范围及工具见 [数据库重置与迁移](docs/database-reset-and-migration.md)。API 和 Provider 设计见 [AI API](docs/ai-api.md) 与 [AI Provider 架构](docs/ai-provider-architecture.md)。
