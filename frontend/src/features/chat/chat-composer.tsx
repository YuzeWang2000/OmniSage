import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { LoaderCircle, Send, Square } from "lucide-react";
import { useEffect, type KeyboardEvent } from "react";

import { getKnowledgeBases } from "@/api/knowledge";
import { queryKeys } from "@/api/query-keys";
import { getWikiStatus, switchWikiMode } from "@/api/settings";
import { getModels } from "@/api/system";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import type { ChatControls } from "@/features/chat/types";

interface ChatComposerProps {
  userId: number;
  value: string;
  controls: ChatControls;
  streaming: boolean;
  hasConversation: boolean;
  onValueChange: (value: string) => void;
  onControlsChange: (changes: Partial<ChatControls>) => void;
  onSubmit: () => void;
  onStop: () => void;
}

export function ChatComposer({
  userId,
  value,
  controls,
  streaming,
  hasConversation,
  onValueChange,
  onControlsChange,
  onSubmit,
  onStop,
}: ChatComposerProps) {
  const queryClient = useQueryClient();
  const models = useQuery({
    queryKey: queryKeys.system.models,
    queryFn: ({ signal }) => getModels(signal),
    staleTime: 5 * 60_000,
  });
  const knowledgeBases = useQuery({
    queryKey: queryKeys.knowledge.all(userId),
    queryFn: ({ signal }) => getKnowledgeBases(userId, { signal }),
    enabled: Boolean(userId && controls.ragEnabled && !controls.wikiEnabled),
  });
  const wiki = useQuery({
    queryKey: queryKeys.settings.wiki,
    queryFn: ({ signal }) => getWikiStatus(signal),
    enabled: controls.wikiEnabled,
    staleTime: 30_000,
  });
  const wikiMode = useMutation({
    mutationFn: (mode: "online" | "offline") => switchWikiMode(mode),
    onSuccess: (response) => queryClient.setQueryData(queryKeys.settings.wiki, response),
  });

  useEffect(() => {
    if (controls.model || !models.data?.all_models.length) return;
    onControlsChange({ model: models.data.all_models[0] });
  }, [controls, models.data?.all_models, onControlsChange]);

  useEffect(() => {
    if (!controls.ragEnabled || controls.wikiEnabled || controls.knowledgeBaseId) return;
    const first = knowledgeBases.data?.[0];
    if (first) onControlsChange({ knowledgeBaseId: first.id });
  }, [
    controls.knowledgeBaseId,
    controls.ragEnabled,
    controls.wikiEnabled,
    knowledgeBases.data,
    onControlsChange,
  ]);

  const requiresKnowledgeBase = controls.ragEnabled && !controls.wikiEnabled;
  const missingKnowledgeBase = requiresKnowledgeBase && !controls.knowledgeBaseId;
  const canSubmit = Boolean(value.trim() && controls.model && !streaming && !missingKnowledgeBase);

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key !== "Enter" || event.shiftKey || event.nativeEvent.isComposing) return;
    event.preventDefault();
    if (canSubmit) onSubmit();
  };

  return (
    <div className="shrink-0 border-t bg-surface/95 px-3 py-3 backdrop-blur sm:px-5">
      <div className="mx-auto max-w-4xl">
        <div className="mb-2 flex min-w-0 flex-wrap items-end gap-2">
          <div className="min-w-[10rem] flex-1 sm:max-w-52">
            <Label htmlFor="chat-model" className="sr-only">
              模型
            </Label>
            <select
              id="chat-model"
              className="h-9 w-full rounded-lg border bg-surface px-2.5 text-xs outline-none focus-visible:border-primary disabled:bg-[#f2f4f7]"
              value={controls.model}
              disabled={streaming || models.isPending}
              onChange={(event) => onControlsChange({ model: event.target.value })}
              aria-label="模型"
            >
              {!controls.model && (
                <option value="">{models.isError ? "模型加载失败" : "选择模型"}</option>
              )}
              {models.data?.local_models.length ? (
                <optgroup label="本地模型">
                  {models.data.local_models.map((model) => (
                    <option key={model} value={model}>
                      {model}
                    </option>
                  ))}
                </optgroup>
              ) : null}
              {models.data?.online_models.length ? (
                <optgroup label="在线模型">
                  {models.data.online_models.map((model) => (
                    <option key={model} value={model}>
                      {model}
                    </option>
                  ))}
                </optgroup>
              ) : null}
            </select>
          </div>

          <label className="flex h-9 items-center gap-2 rounded-lg border px-2.5 text-xs font-medium">
            <Switch
              checked={controls.ragEnabled}
              disabled={streaming}
              onCheckedChange={(ragEnabled) => onControlsChange({ ragEnabled })}
              aria-label="启用 RAG"
              className="h-5 w-9 [&>span]:size-4 [&>span]:data-[state=checked]:translate-x-4"
            />
            RAG
          </label>
          <label className="flex h-9 items-center gap-2 rounded-lg border px-2.5 text-xs font-medium">
            <Switch
              checked={controls.wikiEnabled}
              disabled={streaming}
              onCheckedChange={(wikiEnabled) => onControlsChange({ wikiEnabled })}
              aria-label="启用 Wiki"
              className="h-5 w-9 [&>span]:size-4 [&>span]:data-[state=checked]:translate-x-4"
            />
            Wiki
          </label>

          {requiresKnowledgeBase && (
            <div className="min-w-[11rem] flex-1 sm:max-w-60">
              <Label htmlFor="chat-knowledge-base" className="sr-only">
                知识库
              </Label>
              <select
                id="chat-knowledge-base"
                className="h-9 w-full rounded-lg border bg-surface px-2.5 text-xs outline-none focus-visible:border-primary disabled:bg-[#f2f4f7]"
                value={controls.knowledgeBaseId ?? ""}
                disabled={streaming || knowledgeBases.isPending}
                onChange={(event) =>
                  onControlsChange({ knowledgeBaseId: Number(event.target.value) || null })
                }
              >
                <option value="">{knowledgeBases.isError ? "知识库加载失败" : "选择知识库"}</option>
                {knowledgeBases.data?.map((knowledgeBase) => (
                  <option key={knowledgeBase.id} value={knowledgeBase.id}>
                    {knowledgeBase.name}
                  </option>
                ))}
              </select>
            </div>
          )}

          {controls.wikiEnabled && (
            <div className="flex items-center gap-2">
              <Label htmlFor="chat-wiki-mode" className="sr-only">
                Wiki 模式
              </Label>
              <select
                id="chat-wiki-mode"
                className="h-9 rounded-lg border bg-surface px-2.5 text-xs outline-none focus-visible:border-primary"
                value={wiki.data?.mode === "offline" ? "offline" : "online"}
                disabled={streaming || wiki.isPending || wikiMode.isPending || wiki.isError}
                onChange={(event) => wikiMode.mutate(event.target.value as "online" | "offline")}
              >
                <option value="online">Wiki 在线</option>
                <option value="offline">Wiki 离线</option>
              </select>
              {wiki.data && (
                <Badge tone={wiki.data.success ? "success" : "danger"}>
                  {wiki.data.success ? "可用" : "不可用"}
                </Badge>
              )}
            </div>
          )}
        </div>

        {(models.isError ||
          knowledgeBases.isError ||
          wiki.isError ||
          wikiMode.isError ||
          missingKnowledgeBase) && (
          <p className="mb-2 text-xs text-danger" role="alert">
            {models.isError
              ? "模型列表加载失败，请检查后端服务。"
              : knowledgeBases.isError
                ? "知识库加载失败，请重试。"
                : wiki.isError || wikiMode.isError
                  ? "Wiki 状态或模式更新失败。"
                  : "启用 RAG 后需要选择一个知识库。"}
          </p>
        )}

        <form
          className="flex min-w-0 items-end gap-2 rounded-2xl border bg-surface p-2 shadow-sm focus-within:border-primary focus-within:ring-3 focus-within:ring-primary/10"
          onSubmit={(event) => {
            event.preventDefault();
            if (canSubmit) onSubmit();
          }}
        >
          <Label htmlFor="chat-message" className="sr-only">
            消息
          </Label>
          <textarea
            id="chat-message"
            rows={1}
            className="max-h-40 min-h-11 min-w-0 flex-1 resize-none bg-transparent px-2 py-2.5 text-sm leading-6 outline-none placeholder:text-[#98a2b3]"
            placeholder={
              hasConversation ? "输入问题，Enter 发送，Shift+Enter 换行" : "创建对话后开始提问"
            }
            value={value}
            disabled={!hasConversation || streaming}
            onChange={(event) => onValueChange(event.target.value)}
            onKeyDown={handleKeyDown}
          />
          {streaming ? (
            <Button
              type="button"
              variant="secondary"
              size="icon"
              onClick={onStop}
              aria-label="停止生成"
            >
              <Square className="size-4 fill-current" aria-hidden="true" />
            </Button>
          ) : (
            <Button type="submit" size="icon" disabled={!canSubmit} aria-label="发送消息">
              {models.isPending ? (
                <LoaderCircle className="size-4 animate-spin" />
              ) : (
                <Send className="size-4" />
              )}
            </Button>
          )}
        </form>
        <p className="mt-1.5 text-center text-[10px] text-muted">
          AI 生成内容可能不准确，请核对关键事实与引用原文。
        </p>
      </div>
    </div>
  );
}
