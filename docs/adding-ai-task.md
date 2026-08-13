# 新增 AI Task

在线 Embedding、Rerank、TTS、STT、视觉理解和图像生成目前仅有契约或枚举扩展点，尚无调用实现与前端入口。

新增任务时：定义独立 request/response 与 Adapter Protocol；在 ModelDescriptor 声明 task_types、输入/输出 modality 和 limits；在 Workflow 声明必需/可选模型槽位；执行前验证所有权、available、task、modality、capability 和参数；实现供应商映射与安全错误；最后按 capability 增加 UI，而非按模型名判断。

- Embedding：实现 `EmbeddingRequest/Response`，不得返回空或伪向量。
- Rerank：实现 `RerankRequest/Response`，保持 document id/index。
- TTS：实现 `SpeechSynthesisRequest/Response`，产物必须进入 Asset 服务，不在 JSON 内长期放 Base64。
- STT/视觉/图像：先完成 Asset 所有权、MIME/真实类型、大小/像素/时长、EXIF 与生命周期，再映射 Provider。

每个任务测试：契约验证、错误模态、跨用户 Asset、Adapter 未实现时 UnsupportedTask、取消/超时、无虚假成功，并证明现有 Chat 流不受影响。
