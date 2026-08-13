# OmniSage Backend

```powershell
uv sync --dev
uv run python scripts/create_tables.py
uv run uvicorn main:app --host 127.0.0.1 --port 8000
```

配置从仓库根目录 `.env` 加载，且不会覆盖系统或容器已有的环境变量。DeepSeek 和百炼在线连接必须配置 `CREDENTIAL_ENCRYPTION_KEY`，修改后需重启后端。

百炼北京、新加坡和弗吉尼亚公共端点可不填 Workspace ID；东京和法兰克福当前使用 Workspace 端点，必须填写 Workspace ID。填写 Workspace ID 时会切换到相应地域的 Workspace 端点。

`app/ai/contracts` 定义 ModelDescriptor、ModelTaskType、Modality、ContentPart、任务请求和标准事件；`providers` 包含 Registry 与 Ollama/DeepSeek/DashScope Adapter；`services` 管理连接、加密凭证和模型缓存；`workflows` 做 direct_chat、grounded_chat、agent 依赖与能力校验。路由不调用供应商 SDK。

模型 key 为 `{provider}::{connection_id}::{provider_model_id}`。DeepSeek 用官方 `/models`；Ollama 用 `/api/tags` 和 `/api/show` capabilities；百炼未配置 `manual_models` 时使用 OpenAI-compatible `/models` 完整候选目录，配置后将其作为严格白名单。缓存刷新失败保留旧数据并标记 stale。SSE 事件为 `content_delta`、`reasoning_delta`、`tool_call`、`usage`、`done`、`error`。

DeepSeek 使用 `thinking.type` 与 `reasoning_effort=high|max`，思考开启时过滤 temperature。百炼将 `enable_thinking` 与 `reasoning_effort` 留在 Adapter 内；只有 ModelDescriptor 明确声明能力时才允许发送。Ollama 使用 `/api/chat` NDJSON 并转换为标准事件。

百炼连接测试和刷新使用不产生推理的 `/models` 请求；返回项作为远端候选目录而非逐模型授权证明，并以 `metadata.authorization_unverified=true` 标记。任务与输入输出模态优先读取供应商返回的结构化字段，缺失时按官方文档中的模型族进行保守分类；无法识别则保持空任务和空模态，不默认归为 Chat。配置 `manual_models` 后只暴露白名单项，能力仍可用 `manual_model_capabilities` 显式覆盖。

凭证由 `CREDENTIAL_ENCRYPTION_KEY` 派生 Fernet key 加密，响应不含密文或明文。自定义 Base URL 在 DNS 解析后检查 SSRF。初始化采用 SQLAlchemy metadata；重置见 `scripts/reset_database.py`，不会进入 FastAPI 启动路径，也没有 HTTP 重置端点。

```powershell
uv run pytest -q
uv run python -m compileall -q app scripts tests
uv run python scripts/reset_database.py --dry-run
```

生产环境设置 `APP_ENV=production`。生产重置必须同时提供 `--backup --production-confirm --yes`；SQLite 恢复使用 `--restore-from <同目录且通过完整性检查的 .bak> --yes`，生产恢复还需 `--production-confirm`。2026-08-12 实测后端 `28 passed`，Python compileall 通过。

未实现：在线 Embedding/Rerank、TTS/STT、视觉/图像/视频调用和 Asset 上传。契约已定义，但调用会明确失败且无前端入口。
