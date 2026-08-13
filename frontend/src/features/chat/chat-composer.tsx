import { useQuery } from "@tanstack/react-query";
import { LoaderCircle, Send, Square } from "lucide-react";
import { useEffect, useMemo, type KeyboardEvent } from "react";
import { getModels } from "@/api/system";
import { getKnowledgeBases } from "@/api/knowledge";
import { queryKeys } from "@/api/query-keys";
import { Button } from "@/components/ui/button";
import type { ChatControls } from "@/features/chat/types";
import { useAuthStore } from "@/stores/auth-store";

interface Props { value: string; controls: ChatControls; streaming: boolean; hasConversation: boolean; onValueChange(v:string):void; onControlsChange(v:Partial<ChatControls>):void; onSubmit():void; onStop():void }

export function ChatComposer({value,controls,streaming,hasConversation,onValueChange,onControlsChange,onSubmit,onStop}: Props) {
  const userId = useAuthStore((state) => state.user?.user_id ?? 0);
  const models = useQuery({ queryKey: queryKeys.system.chatModels, queryFn: ({signal}) => getModels(signal, { chatOnly: true }), staleTime: 300_000 });
  const knowledgeBases = useQuery({
    queryKey: queryKeys.knowledge.all(userId),
    queryFn: ({ signal }) => getKnowledgeBases(userId, { signal }),
    enabled: Boolean(userId && controls.workflow === "grounded_chat" && !controls.wikiEnabled),
  });
  const chatModels = useMemo(() => models.data || [], [models.data]);
  const selected = chatModels.find((model) => model.key === controls.modelKey);
  useEffect(() => { if (!controls.modelKey && chatModels[0]) onControlsChange({ modelKey: chatModels[0].key }); }, [chatModels, controls.modelKey, onControlsChange]);
  const retrievalReady = controls.workflow !== "grounded_chat" || controls.wikiEnabled || Boolean(controls.knowledgeBaseId);
  const canSubmit = Boolean(value.trim() && selected && !streaming && retrievalReady);
  const grouped = chatModels.reduce<Map<string, typeof chatModels>>((result, model) => {
    const label = `${model.provider} · ${model.connection_id}`;
    result.set(label, [...(result.get(label) || []), model]);
    return result;
  }, new Map());
  const keyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => { if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) { event.preventDefault(); if (canSubmit) onSubmit(); } };
  return <div className="shrink-0 border-t bg-surface/95 px-3 py-3"><div className="mx-auto max-w-4xl">
    <div className="mb-2 flex flex-wrap gap-2">
      <select aria-label="模型" className="h-9 min-w-52 rounded-lg border bg-surface px-2.5 text-xs" value={controls.modelKey} disabled={streaming || models.isPending} onChange={(e) => onControlsChange({modelKey:e.target.value, reasoning:"auto", reasoningEffort:null, workflow:"direct_chat", ragEnabled:false})}>
        {!controls.modelKey && <option value="">选择模型</option>}
        {[...grouped].map(([label, entries]) => <optgroup key={label} label={label}>{entries.map((model) => <option key={model.key} value={model.key}>{model.display_name}{model.stale ? "（缓存已过期）" : ""}</option>)}</optgroup>)}
      </select>
      {selected?.capabilities.reasoning === true && <select aria-label="推理模式" className="h-9 rounded-lg border bg-surface px-2.5 text-xs" value={controls.reasoning} onChange={(e)=>onControlsChange({reasoning:e.target.value as ChatControls["reasoning"]})} disabled={selected.capabilities.reasoning_toggle === false}><option value="off">不思考</option><option value="auto">自动</option><option value="on">深度思考</option></select>}
      {selected?.capabilities.reasoning_efforts.length ? <select aria-label="推理强度" className="h-9 rounded-lg border bg-surface px-2.5 text-xs" value={controls.reasoningEffort || ""} onChange={(e)=>onControlsChange({reasoningEffort:e.target.value || null})}><option value="">默认强度</option>{selected.capabilities.reasoning_efforts.map((effort)=><option key={effort}>{effort}</option>)}</select> : null}
      <select aria-label="工作流" className="h-9 rounded-lg border bg-surface px-2.5 text-xs" value={controls.workflow} onChange={(e)=>{const workflow=e.target.value as ChatControls["workflow"]; onControlsChange({workflow,ragEnabled:workflow==="grounded_chat"})}}><option value="direct_chat">直接聊天</option><option value="grounded_chat">知识库问答</option><option value="agent" disabled={selected?.capabilities.tools !== true}>Agent（需要工具能力）</option></select>
      {controls.workflow === "grounded_chat" && !controls.wikiEnabled && <select aria-label="知识库" className="h-9 min-w-44 rounded-lg border bg-surface px-2.5 text-xs" value={controls.knowledgeBaseId ?? ""} disabled={streaming || knowledgeBases.isPending} onChange={(e)=>onControlsChange({knowledgeBaseId:e.target.value ? Number(e.target.value) : null})}><option value="">选择知识库</option>{knowledgeBases.data?.map((item)=><option key={item.id} value={item.id}>{item.name}</option>)}</select>}
    </div>
    {models.isError && <p className="mb-2 text-xs text-danger">模型目录加载失败，请在设置中刷新连接模型。</p>}
    {controls.workflow === "grounded_chat" && !controls.wikiEnabled && knowledgeBases.isError && <p className="mb-2 text-xs text-danger">知识库列表加载失败，请稍后重试。</p>}
    {controls.workflow === "grounded_chat" && !controls.wikiEnabled && !knowledgeBases.isPending && !knowledgeBases.isError && !knowledgeBases.data?.length && <p className="mb-2 text-xs text-muted">请先创建并上传一个知识库，再使用知识库问答。</p>}
    <form className="flex items-end gap-2 rounded-2xl border bg-surface p-2" onSubmit={(e)=>{e.preventDefault();if(canSubmit)onSubmit()}}><textarea aria-label="消息" rows={1} className="min-h-11 min-w-0 flex-1 resize-none bg-transparent px-2 py-2.5 text-sm outline-none" placeholder={hasConversation?"输入问题，Enter 发送":"创建对话后开始提问"} value={value} disabled={!hasConversation||streaming} onChange={(e)=>onValueChange(e.target.value)} onKeyDown={keyDown}/>{streaming?<Button type="button" variant="secondary" size="icon" onClick={onStop} aria-label="停止生成"><Square className="size-4"/></Button>:<Button type="submit" size="icon" disabled={!canSubmit} aria-label="发送消息">{models.isPending?<LoaderCircle className="size-4 animate-spin"/>:<Send className="size-4"/>}</Button>}</form>
  </div></div>;
}
