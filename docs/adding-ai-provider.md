# 新增 AI Provider

1. 在 `app/ai/providers/<name>` 实现 Adapter，声明 provider_type、连接测试、模型发现、supports_task 和真实任务方法。
2. 在 Registry 注册，增加严格 Provider/Protocol/Region 枚举与连接字段。
3. 将真实模型响应转为 ModelDescriptor；不按名称推断任务或能力，缺失能力为 null，覆盖表必须版本控制。
4. 在 Adapter 内将 ContentPart、reasoning、usage、tool call、错误映射为供应商格式/标准事件，不向工作流泄漏 extra_body。
5. 增加连接/SSRF/用户隔离、发现/cache stale、流取消、错误脱敏单测；同步 OpenAPI 类型、前端表单和文档。

最小结构（无真实密钥）：

```python
class ExampleProvider:
    provider_type = "example"
    def supports_task(self, task_type): return task_type == ModelTaskType.CHAT
    async def list_models(self, connection, credential): return []
    async def test_connection(self, connection, credential): ...
    async def stream_chat(self, connection, model, request, credential):
        yield AIStreamEvent(type="done")
```

空模型列表只表示实际未发现，不能用硬编码收费模型填充。实现时还要覆盖 reasoning_content、usage、provider rate limit/timeout、能力覆盖表与前端标签。
