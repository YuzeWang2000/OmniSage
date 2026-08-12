import * as Dialog from "@radix-ui/react-dialog";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Menu, MessageSquareText, X } from "lucide-react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { streamChat } from "@/api/chat";
import { ApiError } from "@/api/client";
import {
  createConversation,
  deleteConversation,
  getConversationMessages,
  getConversations,
  renameConversation,
} from "@/api/conversations";
import { queryKeys } from "@/api/query-keys";
import { searchKnowledgeBase, searchWiki } from "@/api/search";
import type { ApiSchemas, Conversation } from "@/api/types";
import { StatusMessage } from "@/components/common/status-message";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ChatComposer } from "@/features/chat/chat-composer";
import { ChatMessages } from "@/features/chat/chat-messages";
import { ConversationPanel } from "@/features/chat/conversation-panel";
import type { ChatCitation, ChatControls, DisplayChatMessage } from "@/features/chat/types";
import { useAuthStore } from "@/stores/auth-store";
import { useChatStore } from "@/stores/chat-store";
import { usePreferencesStore } from "@/stores/preferences-store";

type ChatHistory = ApiSchemas["ChatHistoryResponse"];

interface ChatAttempt {
  id: string;
  prompt: string;
  answer: string;
  kind: "new" | "regenerate";
  status: "streaming" | "error" | "stopped";
  controls: ChatControls;
}

interface MessageExtra {
  citations: ChatCitation[];
  citationError: string | null;
}

const messageExtraKey = (conversationId: number, assistantIndex: number) =>
  `${conversationId}:${assistantIndex}`;

function findLastAssistantIndex(messages: ChatHistory["messages"]) {
  for (let index = messages.length - 1; index >= 0; index -= 1) {
    if (messages[index]?.role === "assistant") return index;
  }
  return -1;
}

function mutationMessage(error: unknown) {
  return error instanceof ApiError ? error.message : "会话操作失败，请重试";
}

export function ChatWorkspace() {
  const userId = useAuthStore((state) => state.user?.user_id ?? 0);
  const activeConversationId = useChatStore((state) => state.activeConversationId);
  const setActiveConversationId = useChatStore((state) => state.setActiveConversationId);
  const initialPreferences = useRef(usePreferencesStore.getState());
  const [searchParams, setSearchParams] = useSearchParams();
  const queryClient = useQueryClient();
  const [mobilePanelOpen, setMobilePanelOpen] = useState(false);
  const [draft, setDraft] = useState("");
  const [attempt, setAttempt] = useState<ChatAttempt | null>(null);
  const [messageExtras, setMessageExtras] = useState<Record<string, MessageExtra>>({});
  const [controls, setControls] = useState<ChatControls>(() => ({
    model: initialPreferences.current.defaultModel,
    ragEnabled: initialPreferences.current.ragEnabled,
    wikiEnabled: initialPreferences.current.wikiEnabled,
    knowledgeBaseId: null,
  }));
  const abortRef = useRef<AbortController | null>(null);

  const conversations = useQuery({
    queryKey: queryKeys.conversations.all(userId),
    queryFn: ({ signal }) => getConversations(userId, { signal }),
    enabled: Boolean(userId),
  });
  const messages = useQuery({
    queryKey: queryKeys.conversations.messages(activeConversationId ?? 0),
    queryFn: ({ signal }) => getConversationMessages(activeConversationId!, signal),
    enabled: Boolean(activeConversationId),
  });

  const selectConversation = useCallback(
    (id: number | null, replace = false) => {
      abortRef.current?.abort();
      abortRef.current = null;
      setAttempt(null);
      if (activeConversationId) {
        void queryClient.cancelQueries({
          queryKey: queryKeys.conversations.messages(activeConversationId),
        });
      }
      setActiveConversationId(id);
      const next = new URLSearchParams();
      if (id) next.set("conversation", String(id));
      setSearchParams(next, { replace });
      setMobilePanelOpen(false);
    },
    [activeConversationId, queryClient, setActiveConversationId, setSearchParams],
  );

  useEffect(() => {
    const requested = Number(searchParams.get("conversation"));
    if (Number.isInteger(requested) && requested > 0 && requested !== activeConversationId) {
      setActiveConversationId(requested);
    }
  }, [activeConversationId, searchParams, setActiveConversationId]);

  useEffect(() => {
    if (!conversations.data) return;
    const stillExists = conversations.data.some(({ id }) => id === activeConversationId);
    if (stillExists) return;
    if (!conversations.data.length && activeConversationId === null) return;
    selectConversation(conversations.data[0]?.id ?? null, true);
  }, [activeConversationId, conversations.data, selectConversation]);

  useEffect(() => () => abortRef.current?.abort(), []);

  const createConversationMutation = useMutation({
    mutationFn: () => createConversation(),
    onSuccess: (conversation) => {
      queryClient.setQueryData<Conversation[]>(
        queryKeys.conversations.all(userId),
        (current = []) => [conversation, ...current],
      );
      selectConversation(conversation.id);
    },
  });
  const renameConversationMutation = useMutation({
    mutationFn: ({ id, title }: { id: number; title: string }) => renameConversation(id, title),
    onSuccess: (response, variables) => {
      queryClient.setQueryData<Conversation[]>(
        queryKeys.conversations.all(userId),
        (current = []) =>
          current.map((conversation) =>
            conversation.id === variables.id
              ? { ...conversation, title: response.title }
              : conversation,
          ),
      );
    },
  });
  const deleteConversationMutation = useMutation({
    mutationFn: (id: number) => deleteConversation(id),
    onSuccess: (_, deletedId) => {
      const remaining = (conversations.data || []).filter(({ id }) => id !== deletedId);
      queryClient.setQueryData(queryKeys.conversations.all(userId), remaining);
      queryClient.removeQueries({ queryKey: queryKeys.conversations.messages(deletedId) });
      if (activeConversationId === deletedId) selectConversation(remaining[0]?.id ?? null, true);
    },
  });

  const loadCitations = useCallback(
    async (prompt: string, snapshot: ChatControls, signal: AbortSignal) => {
      if (snapshot.wikiEnabled) {
        const response = await searchWiki(prompt, { limit: 5, signal });
        return response.results.map<ChatCitation>((result, index) => ({
          id: `wiki-${index}-${result.title}`,
          title: result.title,
          excerpt: result.content,
          kind: "wiki",
          source: response.mode === "offline" ? "维基百科（离线）" : "维基百科（在线）",
          score: result.score,
          url: result.url,
        }));
      }
      if (snapshot.ragEnabled && snapshot.knowledgeBaseId) {
        const response = await searchKnowledgeBase(snapshot.knowledgeBaseId, prompt, {
          topK: 5,
          signal,
        });
        return response.results.map<ChatCitation>((result, index) => ({
          id: `kb-${snapshot.knowledgeBaseId}-${index}`,
          title: result.source || response.knowledge_base_name,
          excerpt: result.content,
          kind: "knowledge",
          source: result.source || response.knowledge_base_name,
          page: result.page,
          section: result.section,
          score: result.score,
        }));
      }
      return [];
    },
    [],
  );

  const startGeneration = useCallback(
    async (prompt: string, kind: "new" | "regenerate") => {
      if (!activeConversationId || !prompt.trim() || messages.isPending) return;
      const conversationId = activeConversationId;
      const snapshot = { ...controls };
      const attemptId = `${conversationId}-${Date.now()}`;
      const controller = new AbortController();
      abortRef.current?.abort();
      abortRef.current = controller;
      setAttempt({
        id: attemptId,
        prompt: prompt.trim(),
        answer: "",
        kind,
        status: "streaming",
        controls: snapshot,
      });
      if (kind === "new") setDraft("");
      let answer = "";

      try {
        await streamChat(
          {
            conversation_id: conversationId,
            message: prompt.trim(),
            model: snapshot.model,
            mode: "chat",
            use_rag: snapshot.ragEnabled,
            use_wiki: snapshot.wikiEnabled,
            knowledge_base_id: snapshot.knowledgeBaseId,
            stream: true,
            regenerate: kind === "regenerate",
            chain_type: "stuff",
            prompt_name: "chat_default",
            use_reranker: true,
            top_k: 5,
            score_threshold: 0.5,
          },
          {
            signal: controller.signal,
            onChunk: (chunk) => {
              answer += chunk;
              setAttempt((current) =>
                current?.id === attemptId ? { ...current, answer } : current,
              );
            },
          },
        );

        const previous = queryClient.getQueryData<ChatHistory>(
          queryKeys.conversations.messages(conversationId),
        ) || { conversation_id: conversationId, messages: [] };
        const nextMessages = [...previous.messages];
        let assistantIndex: number;
        if (kind === "regenerate") {
          assistantIndex = findLastAssistantIndex(nextMessages);
          if (assistantIndex < 0)
            throw new ApiError("没有可重新生成的回答", { kind: "validation" });
          nextMessages[assistantIndex] = { role: "assistant", content: answer };
        } else {
          nextMessages.push({ role: "user", content: prompt.trim() });
          assistantIndex = nextMessages.length;
          nextMessages.push({ role: "assistant", content: answer });
        }
        queryClient.setQueryData<ChatHistory>(queryKeys.conversations.messages(conversationId), {
          conversation_id: conversationId,
          messages: nextMessages,
        });

        let citations: ChatCitation[] = [];
        let citationError: string | null = null;
        if (snapshot.ragEnabled || snapshot.wikiEnabled) {
          try {
            citations = await loadCitations(prompt.trim(), snapshot, controller.signal);
            if (!citations.length) citationError = "回答已生成，但没有检索到可展示的引用来源。";
          } catch (error) {
            if (!(error instanceof ApiError && error.kind === "cancelled")) {
              citationError = "回答已生成，但引用来源暂时无法加载。";
            }
          }
        }
        setMessageExtras((current) => ({
          ...current,
          [messageExtraKey(conversationId, assistantIndex)]: { citations, citationError },
        }));
        setAttempt((current) => (current?.id === attemptId ? null : current));
        void queryClient.invalidateQueries({ queryKey: queryKeys.conversations.all(userId) });
      } catch (error) {
        const cancelled = error instanceof ApiError && error.kind === "cancelled";
        setAttempt((current) =>
          current?.id === attemptId
            ? { ...current, answer, status: cancelled ? "stopped" : "error" }
            : current,
        );
      } finally {
        if (abortRef.current === controller) abortRef.current = null;
      }
    },
    [activeConversationId, controls, loadCitations, messages.isPending, queryClient, userId],
  );

  const displayMessages = useMemo(() => {
    const source = messages.data?.messages || [];
    const lastAssistantIndex = findLastAssistantIndex(source);
    const display = source.map<DisplayChatMessage>((message, index) => {
      const extra = activeConversationId
        ? messageExtras[messageExtraKey(activeConversationId, index)]
        : undefined;
      return {
        id: `server-${activeConversationId}-${index}`,
        role: message.role === "user" ? "user" : "assistant",
        content: message.content,
        citations: extra?.citations,
        citationError: extra?.citationError,
        canRegenerate: !attempt && index === lastAssistantIndex && message.role === "assistant",
      };
    });

    if (attempt?.kind === "regenerate" && lastAssistantIndex >= 0) {
      display[lastAssistantIndex] = {
        id: attempt.id,
        role: "assistant",
        content: attempt.answer,
        status: attempt.status,
      };
    } else if (attempt) {
      display.push({ id: `${attempt.id}-user`, role: "user", content: attempt.prompt });
      display.push({
        id: `${attempt.id}-assistant`,
        role: "assistant",
        content: attempt.answer,
        status: attempt.status,
      });
    }
    return display;
  }, [activeConversationId, attempt, messageExtras, messages.data?.messages]);

  const lastServerPrompt = useMemo(() => {
    const source = messages.data?.messages || [];
    const assistantIndex = findLastAssistantIndex(source);
    if (assistantIndex < 1) return null;
    const candidate = source[assistantIndex - 1];
    return candidate?.role === "user" ? candidate.content : null;
  }, [messages.data?.messages]);

  const activeConversation = conversations.data?.find(({ id }) => id === activeConversationId);
  const updateControls = useCallback((changes: Partial<ChatControls>) => {
    setControls((current) => ({ ...current, ...changes }));
  }, []);
  const operationError =
    createConversationMutation.error ||
    renameConversationMutation.error ||
    deleteConversationMutation.error;
  const panelProps = {
    conversations: conversations.data || [],
    activeId: activeConversationId,
    loading: conversations.isPending,
    error: conversations.isError,
    creating: createConversationMutation.isPending,
    mutating: renameConversationMutation.isPending || deleteConversationMutation.isPending,
    onRetry: () => void conversations.refetch(),
    onCreate: () => createConversationMutation.mutate(),
    onSelect: (id: number) => selectConversation(id),
    onRename: (id: number, title: string) => renameConversationMutation.mutate({ id, title }),
    onDelete: (id: number) => deleteConversationMutation.mutate(id),
  };

  return (
    <div className="flex h-full min-h-0 min-w-0 overflow-hidden border-x bg-surface lg:my-3 lg:h-[calc(100%-1.5rem)] lg:rounded-2xl lg:border lg:shadow-xs">
      <aside className="hidden w-72 shrink-0 border-r xl:block" aria-label="会话列表">
        <ConversationPanel {...panelProps} />
      </aside>

      <section className="flex min-w-0 flex-1 flex-col" aria-label="智能对话">
        <header className="flex min-h-14 shrink-0 items-center gap-3 border-b px-3 sm:px-5">
          <Button
            variant="ghost"
            size="icon"
            className="xl:hidden"
            onClick={() => setMobilePanelOpen(true)}
            aria-label="打开会话列表"
          >
            <Menu className="size-5" aria-hidden="true" />
          </Button>
          <span className="grid size-8 shrink-0 place-items-center rounded-xl bg-[#eaf4f0] text-primary">
            <MessageSquareText className="size-4" aria-hidden="true" />
          </span>
          <div className="min-w-0 flex-1">
            <h1 className="truncate text-sm font-semibold">
              {activeConversation?.title || "智能对话"}
            </h1>
            <p className="truncate text-[11px] text-muted">
              {activeConversation
                ? `${activeConversation.message_count} 条历史消息`
                : "选择或创建对话"}
            </p>
          </div>
          {attempt?.status === "streaming" && <Badge tone="success">正在生成</Badge>}
        </header>

        {operationError && (
          <div className="shrink-0 px-3 pt-3 sm:px-5">
            <StatusMessage tone="error">{mutationMessage(operationError)}</StatusMessage>
          </div>
        )}

        <ChatMessages
          messages={displayMessages}
          loading={Boolean(activeConversationId && messages.isPending)}
          error={messages.isError}
          hasConversation={Boolean(activeConversationId)}
          onRetryLoad={() => void messages.refetch()}
          onCreateConversation={() => createConversationMutation.mutate()}
          onRegenerate={() => {
            if (lastServerPrompt) void startGeneration(lastServerPrompt, "regenerate");
          }}
          onRetryGeneration={() => {
            if (attempt) void startGeneration(attempt.prompt, attempt.kind);
          }}
        />
        <ChatComposer
          userId={userId}
          value={draft}
          controls={controls}
          streaming={attempt?.status === "streaming"}
          hasConversation={Boolean(activeConversationId)}
          onValueChange={setDraft}
          onControlsChange={updateControls}
          onSubmit={() => void startGeneration(draft, "new")}
          onStop={() => abortRef.current?.abort()}
        />
      </section>

      <Dialog.Root open={mobilePanelOpen} onOpenChange={setMobilePanelOpen}>
        <Dialog.Portal>
          <Dialog.Overlay className="fixed inset-0 z-50 bg-[#101828]/45 backdrop-blur-[2px]" />
          <Dialog.Content className="fixed inset-y-0 left-0 z-50 w-[min(88vw,20rem)] border-r bg-surface shadow-2xl outline-none">
            <Dialog.Title className="sr-only">会话列表</Dialog.Title>
            <Dialog.Description className="sr-only">
              选择、新建、重命名或删除对话
            </Dialog.Description>
            <Dialog.Close asChild>
              <Button
                variant="ghost"
                size="icon"
                className="absolute right-2 top-2 z-10"
                aria-label="关闭会话列表"
              >
                <X className="size-4" aria-hidden="true" />
              </Button>
            </Dialog.Close>
            <ConversationPanel {...panelProps} />
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>
    </div>
  );
}
