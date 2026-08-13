# AI API

OpenAPI `openapi.json` 是事实来源。所有 `/ai/*` 和 `/chat/stream` 要求 Bearer Token，user_id 不从请求体采信。

- `GET /ai/providers`
- `GET|POST /ai/connections`
- `GET|PUT|DELETE /ai/connections/{connection_id}`
- `POST /ai/connections/{connection_id}/test`
- `GET /ai/connections/{connection_id}/models`
- `POST /ai/connections/{connection_id}/models/refresh`
- `GET /ai/models`：支持 connection_id、provider、task_type、input_modality、output_modality、available_only
- `GET /ai/models/{model_key}`

创建连接示例：

```json
{"provider":"deepseek","display_name":"个人 DeepSeek","api_key":"replace-with-secret","manual_models":[],"is_active":true}
```

响应只含 `has_credential`、`masked_credential`、`credential_version`，不含明文或密文。

聊天请求：

```json
{"conversation_id":1,"messages":[{"role":"user","content":[{"type":"text","text":"你好"}],"metadata":{}}],"model_key":"deepseek::connection-id::provider-model-id","workflow":"direct_chat","options":{"reasoning":"auto","reasoning_effort":null,"structured_output":false,"tools":[]},"retrieval":{"enabled":false,"wiki":false,"knowledge_base_id":null,"use_reranker":true,"top_k":5,"score_threshold":0.5},"model_slots":{"generation_model_key":null,"embedding_model_key":null,"rerank_model_key":null,"speech_model_key":null},"regenerate":false}
```

ContentPart 支持 text/image/audio/video/document/tool_result 的 Schema；当前只有 text 可调用。SSE `data` JSON 使用 `type`，例如 `{"type":"content_delta","content":"你好"}`、`{"type":"usage","input_tokens":10,"output_tokens":4}`、`{"type":"done"}`。错误为 `{"error":{"code":"UnsupportedCapability","message":"..."}}` 或流内 `type=error`，HTTP 映射 400/404/409/422/429/503/504。

已删除旧 `/models`、`/api-keys/*`、裸 `model`、`message: string`、`mode/use_rag/use_wiki` 和旧 chunk SSE；这是破坏性变化。

## 当前错误与百炼能力覆盖

HTTP 错误映射包括 400、401、404、409、422、429、502、503、504。供应商畸形 JSON/SSE 映射为 `ProviderInvalidResponse`（502），响应不会包含供应商原始错误体。

百炼刷新会读取兼容端点 `/models` 并把结果作为候选目录；`manual_models` 为空时返回全部候选，非空时仅返回该白名单。远端候选项的 `metadata.authorization_unverified` 为 `true`，表示仍需实际调用验证权限。任务和模态优先使用响应元数据，缺失时按官方模型族规则分类，无法识别时保持为空；`manual_model_capabilities` 可按模型 ID 显式覆盖 nullable capability。DeepSeek 始终使用官方动态 `/models` 结果。Reasoning SSE 与 content SSE 分流，前端仅在当前请求中展示推理文本，不写入会话历史。

OmniSage 用户认证失败使用 HTTP 401；上游供应商拒绝其 API Key 使用 `CredentialInvalid` 与 HTTP 424，前端不得因此清除用户登录状态。

`grounded_chat` 必须设置 `retrieval.enabled=true`，并在非 Wiki 模式提供 `knowledge_base_id`。缺少选择在请求模型校验阶段返回 422；知识库不存在或不属于当前用户返回 `KnowledgeBaseNotFound` 404，不得抛出未处理异常。
