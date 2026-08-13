import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";

import {
  createConnection,
  deleteConnection,
  getConnections,
  refreshConnectionModels,
  testConnection,
  updateConnection,
  type ConnectionPayload,
} from "@/api/settings";
import { getModels, type ModelCapabilities } from "@/api/system";
import { ApiError } from "@/api/client";
import { queryKeys } from "@/api/query-keys";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

const initial: ConnectionPayload = {
  provider: "ollama",
  display_name: "本地 Ollama",
  region: null,
  workspace_id: null,
  base_url: "http://localhost:11434",
  api_key: null,
  manual_models: [],
  manual_model_capabilities: {},
  is_active: true,
};

const capabilityLabels: Array<[keyof ModelCapabilities, string]> = [
  ["reasoning", "推理"],
  ["tools", "工具"],
  ["structured_output", "结构化输出"],
];

const taskLabels: Record<string, string> = {
  chat: "对话", text_generation: "文本生成", embedding: "向量嵌入", rerank: "重排序",
  text_to_speech: "语音合成", speech_to_text: "语音识别", image_understanding: "图像理解",
  image_generation: "图像生成", video_understanding: "视频理解", video_generation: "视频生成",
};

const modalityLabels: Record<string, string> = {
  text: "文本", image: "图片", audio: "音频", video: "视频", document: "文档",
};

function errorMessage(error: unknown) {
  return error instanceof Error ? error.message : "操作失败，请重试";
}

function fieldError(error: unknown, field: string) {
  if (!(error instanceof ApiError)) return null;
  return error.fieldErrors?.[field] || error.fieldErrors?.form || null;
}

export function ProviderConnections() {
  const queryClient = useQueryClient();
  const [form, setForm] = useState(initial);
  const [manual, setManual] = useState("");
  const [manualCapabilities, setManualCapabilities] = useState<ModelCapabilities>({ reasoning_efforts: [] });
  const [rotationKeys, setRotationKeys] = useState<Record<string, string>>({});
  const list = useQuery({ queryKey: queryKeys.settings.connections, queryFn: ({ signal }) => getConnections(signal) });
  const models = useQuery({ queryKey: queryKeys.system.models, queryFn: ({ signal }) => getModels(signal) });
  const refreshQueries = () => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.settings.connections });
    void queryClient.invalidateQueries({ queryKey: queryKeys.system.models });
  };
  const manualIds = useMemo(() => manual.split(",").map((value) => value.trim()).filter(Boolean), [manual]);
  const create = useMutation({
    mutationFn: () => createConnection({
      ...form,
      display_name: form.display_name.trim(),
      region: form.region?.trim() || null,
      workspace_id: form.workspace_id?.trim() || null,
      base_url: form.base_url?.trim() || null,
      api_key: form.api_key?.trim() || null,
      manual_models: manualIds,
      manual_model_capabilities: Object.fromEntries(manualIds.map((id) => [id, manualCapabilities])),
    }),
    onSuccess: () => {
      refreshQueries();
      setForm(initial);
      setManual("");
      setManualCapabilities({ reasoning_efforts: [] });
    },
  });
  const remove = useMutation({ mutationFn: (id: string) => deleteConnection(id), onSuccess: refreshQueries });
  const test = useMutation({ mutationFn: (id: string) => testConnection(id), onSuccess: refreshQueries });
  const sync = useMutation({ mutationFn: (id: string) => refreshConnectionModels(id), onSuccess: refreshQueries });
  const rotate = useMutation({
    mutationFn: ({ id, apiKey }: { id: string; apiKey: string }) => updateConnection(id, { api_key: apiKey }),
    onSuccess: (_, { id }) => {
      setRotationKeys((current) => ({ ...current, [id]: "" }));
      refreshQueries();
    },
  });
  const operationError = create.error || remove.error || test.error || sync.error || rotate.error;

  return (
    <section className="rounded-2xl border bg-surface">
      <div className="border-b px-5 py-4">
        <h2 className="font-semibold">供应商连接</h2>
        <p className="mt-1 text-xs text-muted">密钥仅在服务端加密保存；轮换时不会读取旧密钥。</p>
      </div>
      <div className="space-y-5 p-5">
        <div className="grid gap-2 sm:grid-cols-2">
          <select
            aria-label="供应商"
            className="h-10 rounded-lg border px-3"
            value={form.provider}
            onChange={(event) => {
              const provider = event.target.value as ConnectionPayload["provider"];
              setForm({
                ...initial,
                provider,
                display_name: provider === "ollama" ? "本地 Ollama" : provider === "deepseek" ? "DeepSeek" : "阿里云百炼",
                base_url: provider === "ollama" ? "http://localhost:11434" : null,
              });
              setManual("");
            }}
          >
            <option value="ollama">Ollama</option>
            <option value="deepseek">DeepSeek</option>
            <option value="dashscope">阿里云百炼</option>
          </select>
          <input aria-label="连接名称" className="h-10 rounded-lg border px-3" value={form.display_name} onChange={(event) => setForm({ ...form, display_name: event.target.value })} />
          {form.provider === "dashscope" && (
            <>
              <label className="space-y-1 text-xs font-medium">
                <span>服务地域 <span className="text-danger">*</span></span>
                <select aria-label="服务地域" className="h-10 w-full rounded-lg border px-3" value={form.region || ""} onChange={(event) => setForm({ ...form, region: event.target.value, workspace_id: "" })}>
                  <option value="">请选择服务地域</option>
                  <option value="cn-beijing">北京（Workspace 可选）</option>
                  <option value="ap-southeast-1">新加坡（Workspace 可选）</option>
                  <option value="us-east-1">弗吉尼亚（无需 Workspace）</option>
                  <option value="ap-northeast-1">东京（需要 Workspace）</option>
                  <option value="eu-central-1">法兰克福（需要 Workspace）</option>
                </select>
                {fieldError(create.error, "region") && <span className="block text-danger">{fieldError(create.error, "region")}</span>}
              </label>
              <label className="space-y-1 text-xs font-medium">
                <span>Workspace ID <span className="font-normal text-muted">（北京/新加坡可不填）</span></span>
                <input aria-label="Workspace ID" placeholder="例如 ws-xxxxxxxx" className="h-10 w-full rounded-lg border px-3" value={form.workspace_id || ""} onChange={(event) => setForm({ ...form, workspace_id: event.target.value })} />
                {fieldError(create.error, "workspace_id") && <span className="block text-danger">{fieldError(create.error, "workspace_id")}</span>}
              </label>
              <label className="space-y-1 text-xs font-medium sm:col-span-2">
                <span>模型白名单 <span className="font-normal text-muted">（可选；留空获取全部候选）</span></span>
                <input aria-label="模型白名单" placeholder="填写后只显示这些模型，多个 ID 用逗号分隔" className="h-10 w-full rounded-lg border px-3" value={manual} onChange={(event) => setManual(event.target.value)} />
              </label>
              <fieldset className="flex flex-wrap gap-3 rounded-lg border p-3 text-xs sm:col-span-2">
                <legend className="px-1 text-muted">手工模型能力（不按模型名猜测）</legend>
                {capabilityLabels.map(([key, label]) => (
                  <label key={key} className="flex items-center gap-1.5">
                    <input type="checkbox" checked={manualCapabilities[key] === true} onChange={(event) => setManualCapabilities({ ...manualCapabilities, [key]: event.target.checked })} />
                    {label}
                  </label>
                ))}
              </fieldset>
            </>
          )}
          {form.provider !== "ollama" && (
            <label className="space-y-1 text-xs font-medium sm:col-span-2">
              <span>{form.provider === "deepseek" ? "DeepSeek API Key" : "阿里云百炼 API Key"} <span className="text-danger">*</span></span>
              <input aria-label="API Key" type="password" autoComplete="new-password" placeholder={form.provider === "deepseek" ? "输入 DeepSeek API Key" : "输入所选地域对应的百炼 API Key"} className="h-10 w-full rounded-lg border px-3" value={form.api_key || ""} onChange={(event) => setForm({ ...form, api_key: event.target.value })} />
              <span className="block font-normal text-muted">密钥只会发送到 OmniSage 后端并加密保存，不会在列表中完整显示。</span>
              {fieldError(create.error, "api_key") && <span className="block text-danger">{fieldError(create.error, "api_key")}</span>}
            </label>
          )}
          {fieldError(create.error, "display_name") && <p className="text-xs text-danger sm:col-span-2">连接名称：{fieldError(create.error, "display_name")}</p>}
          <Button disabled={create.isPending} onClick={() => create.mutate()}>添加连接</Button>
        </div>

        {operationError && <p role="alert" className="text-sm text-danger">{errorMessage(operationError)}；表单内容已保留。</p>}
        {list.isError && <p className="text-sm text-danger">连接列表加载失败，表单内容已保留。</p>}
        <ul className="space-y-3">
          {list.data?.map((connection) => {
            const connectionModels = models.data?.filter((model) => model.connection_id === connection.id) || [];
            return (
              <li key={connection.id} className="rounded-xl border p-4">
                <div className="flex flex-wrap items-center gap-2">
                  <strong>{connection.display_name}</strong>
                  <Badge>{connection.provider}</Badge>
                  {!connection.is_active && <Badge tone="warning">已禁用</Badge>}
                  {connection.last_test_status && <Badge tone={connection.last_test_status === "success" ? "success" : "danger"}>{connection.last_test_status}</Badge>}
                </div>
                <p className="mt-1 break-all text-xs text-muted">{connection.region || "本地"} · {connection.masked_credential || "无需密钥"} · 凭证版本 {connection.credential_version}</p>
                {connection.last_test_message && <p className="mt-1 text-xs text-muted">{connection.last_test_message}</p>}
                <div className="mt-3 flex flex-wrap gap-2">
                  <Button size="sm" variant="secondary" onClick={() => test.mutate(connection.id)}>测试连接</Button>
                  <Button size="sm" variant="secondary" onClick={() => sync.mutate(connection.id)}>刷新模型</Button>
                  <Button size="sm" variant="ghost" onClick={() => remove.mutate(connection.id)}>删除</Button>
                </div>
                {connection.provider !== "ollama" && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    <input aria-label={`轮换 ${connection.display_name} API Key`} type="password" autoComplete="new-password" placeholder="输入新 Key" className="h-9 min-w-52 flex-1 rounded-lg border px-3 text-xs" value={rotationKeys[connection.id] || ""} onChange={(event) => setRotationKeys((current) => ({ ...current, [connection.id]: event.target.value }))} />
                    <Button size="sm" variant="secondary" disabled={!rotationKeys[connection.id]} onClick={() => rotate.mutate({ id: connection.id, apiKey: rotationKeys[connection.id]! })}>轮换 Key</Button>
                  </div>
                )}
                <div className="mt-3 space-y-2" aria-label={`${connection.display_name} 模型目录`}>
                  {connectionModels.map((model) => (
                    <div key={model.key} className="rounded-lg bg-[#f8faf9] p-2.5 text-xs">
                      <div className="flex flex-wrap items-center gap-2"><span className="font-medium">{model.display_name}</span><Badge>{model.source}</Badge>{model.metadata?.authorization_unverified === true && <Badge tone="warning">权限待调用验证</Badge>}{model.stale && <Badge tone="warning">stale</Badge>}</div>
                      <div className="mt-1 flex flex-wrap gap-1">{model.task_types.map((task) => <Badge key={task}>{taskLabels[task] || task}</Badge>)}{!model.task_types.length && <Badge tone="warning">任务类型未知</Badge>}{capabilityLabels.filter(([key]) => model.capabilities[key] === true).map(([key, label]) => <Badge key={key} tone="success">{label}</Badge>)}</div>
                      <p className="mt-1 text-muted">输入：{model.input_modalities.map((item) => modalityLabels[item] || item).join("、") || "未知"} · 输出：{model.output_modalities.map((item) => modalityLabels[item] || item).join("、") || "未知"}</p>
                    </div>
                  ))}
                  {!models.isPending && !connectionModels.length && <p className="text-xs text-muted">尚无模型缓存，请点击“刷新模型”自动获取；供应商未返回的自定义模型可在创建连接时补充。</p>}
                </div>
              </li>
            );
          })}
        </ul>
      </div>
    </section>
  );
}
