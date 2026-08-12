import { ArrowDown, MessageSquareText, Plus } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";

import { EmptyState } from "@/components/common/empty-state";
import { QueryError } from "@/components/common/query-error";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ChatMessage } from "@/features/chat/chat-message";
import type { DisplayChatMessage } from "@/features/chat/types";

interface ChatMessagesProps {
  messages: DisplayChatMessage[];
  loading: boolean;
  error: boolean;
  hasConversation: boolean;
  onRetryLoad: () => void;
  onCreateConversation: () => void;
  onRegenerate: () => void;
  onRetryGeneration: () => void;
}

export function ChatMessages({
  messages,
  loading,
  error,
  hasConversation,
  onRetryLoad,
  onCreateConversation,
  onRegenerate,
  onRetryGeneration,
}: ChatMessagesProps) {
  const viewportRef = useRef<HTMLDivElement>(null);
  const [following, setFollowing] = useState(true);
  const lastSignature = useMemo(() => {
    const last = messages.at(-1);
    return `${messages.length}:${last?.id || ""}:${last?.content.length || 0}`;
  }, [messages]);

  useEffect(() => {
    if (!following) return;
    const viewport = viewportRef.current;
    if (viewport) viewport.scrollTop = viewport.scrollHeight;
  }, [following, lastSignature]);

  const scrollToBottom = () => {
    const viewport = viewportRef.current;
    if (viewport) viewport.scrollTo({ top: viewport.scrollHeight, behavior: "smooth" });
    setFollowing(true);
  };

  return (
    <div className="relative min-h-0 flex-1">
      <div
        ref={viewportRef}
        className="h-full overflow-y-auto overscroll-contain"
        onScroll={(event) => {
          const element = event.currentTarget;
          setFollowing(element.scrollHeight - element.scrollTop - element.clientHeight < 96);
        }}
      >
        {loading ? (
          <div className="mx-auto max-w-4xl space-y-6 px-4 py-8 sm:px-6">
            <Skeleton className="ml-auto h-20 w-2/3 rounded-2xl" />
            <div className="flex gap-4">
              <Skeleton className="size-9 rounded-xl" />
              <Skeleton className="h-32 flex-1 rounded-2xl" />
            </div>
          </div>
        ) : error ? (
          <div className="mx-auto max-w-2xl px-4 py-10">
            <QueryError message="对话消息加载失败" onRetry={onRetryLoad} />
          </div>
        ) : !hasConversation ? (
          <div className="grid h-full place-items-center px-4 py-10">
            <EmptyState
              icon={MessageSquareText}
              title="创建一段新对话"
              description="选择模型和知识来源，然后输入你的第一个问题。"
              action={
                <Button onClick={onCreateConversation}>
                  <Plus className="size-4" />
                  新建对话
                </Button>
              }
            />
          </div>
        ) : messages.length ? (
          <div className="divide-y divide-[#edf0f2] pb-5">
            {messages.map((message, index) => (
              <ChatMessage
                key={message.id}
                message={message}
                onRegenerate={index === messages.length - 1 ? onRegenerate : undefined}
                onRetry={index === messages.length - 1 ? onRetryGeneration : undefined}
              />
            ))}
          </div>
        ) : (
          <div className="grid h-full place-items-center px-4 py-10">
            <EmptyState
              icon={MessageSquareText}
              title="准备好开始了"
              description="消息只会发送给你配置的 OmniSage 后端和所选模型服务。"
            />
          </div>
        )}
      </div>
      {!following && messages.length > 0 && (
        <Button
          type="button"
          variant="secondary"
          size="icon"
          className="absolute bottom-3 left-1/2 z-10 size-10 min-h-10 -translate-x-1/2 rounded-full shadow-lg"
          onClick={scrollToBottom}
          aria-label="回到最新消息"
        >
          <ArrowDown className="size-4" aria-hidden="true" />
        </Button>
      )}
    </div>
  );
}
