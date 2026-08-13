# Changelog

## 1.0.0 - major breaking change

- 新增：Provider Registry、Ollama/DeepSeek/百炼 Adapter、连接 CRUD/测试、模型缓存、标准契约/SSE、凭证加密、SSRF 防护和安全重置工具。
- 修改：聊天使用 ContentPart、model_key、workflow、reasoning；grounded_chat 使用现有本地 Embedding/Reranker 与所选生成模型；前端按连接分组并能力驱动。
- 删除：旧 `/models`、`/api-keys/*`、`llm_service.py`、硬编码在线别名、名称前缀 Provider 判断、旧 ChatRequest 与 chunk SSE。
- 数据库：运行时由 `provider_connections`、`ai_model_cache`、`chat_messages` 替代旧 `user_api_keys`、`chat_history`。升级需备份并显式重置。
- 安全：Key 加密且不回显，自定义端点 DNS/SSRF 校验，错误脱敏。
- 安全：生产数据库重置要求已验证备份与额外确认；SQLite 提供受控恢复；修复旧重置工具 metadata 为空时虚假成功的问题。
- 前端：连接目录展示 source/stale/task/capability，支持 Key 轮换与百炼显式能力覆盖；reasoning/content 分流展示且不持久化完整推理文本。
- 百炼刷新在未指定模型时展示兼容 `/models` 全部候选，指定后执行严格白名单；目录按任务类型与输入输出模态分类，候选权限仍需实际调用验证。
- 区分 OmniSage 登录 401 与供应商 API Key 拒绝 424，测试连接或刷新失败不再错误注销用户。
- 知识库问答增加知识库选择和提交前校验；缺失知识库返回标准 422，不存在或越权返回 404，不再产生 500。
- 修复删除当前或最后一个会话时 URL 查询参数与活动会话状态竞争导致的全局错误页；删除后原子切换到下一会话或空状态。
- 限制：无在线 Embedding/Rerank、TTS/STT、视觉/媒体；无 PostgreSQL/Alembic。
