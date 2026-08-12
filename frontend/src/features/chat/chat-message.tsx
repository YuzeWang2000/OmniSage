import { Bot, ExternalLink, RefreshCcw, UserRound } from "lucide-react";
import { memo } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { SafeMarkdown } from "@/features/chat/safe-markdown";
import type { ChatCitation, DisplayChatMessage } from "@/features/chat/types";
import { cn } from "@/utils/cn";

function safeHttpUrl(value?: string | null) {
  if (!value) return null;
  try {
    const url = new URL(value);
    return url.protocol === "http:" || url.protocol === "https:" ? url.toString() : null;
  } catch {
    return null;
  }
}

function CitationCard({ citation, index }: { citation: ChatCitation; index: number }) {
  const href = safeHttpUrl(citation.url);
  return (
    <li className="rounded-xl border bg-surface p-3.5">
      <div className="flex min-w-0 items-start gap-3">
        <span className="grid size-6 shrink-0 place-items-center rounded-full bg-[#eaf4f0] text-[11px] font-semibold text-primary">
          {index + 1}
        </span>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <p className="min-w-0 truncate text-xs font-semibold">{citation.title}</p>
            <Badge tone="neutral" className="min-h-5 px-2 py-0 text-[10px]">
              {citation.kind === "wiki" ? "Wiki" : "知识库"}
            </Badge>
          </div>
          <p className="mt-1.5 line-clamp-3 whitespace-pre-wrap text-xs leading-5 text-muted">
            {citation.excerpt}
          </p>
          <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-muted">
            {citation.source && <span>来源：{citation.source}</span>}
            {citation.page != null && <span>第 {citation.page} 页</span>}
            {citation.section && <span>章节：{citation.section}</span>}
            {citation.score != null && <span>相关度 {(citation.score * 100).toFixed(1)}%</span>}
            {href && (
              <a
                href={href}
                target="_blank"
                rel="noopener noreferrer nofollow"
                className="inline-flex items-center gap-1 font-medium text-primary hover:underline"
              >
                查看来源
                <ExternalLink className="size-3" aria-hidden="true" />
              </a>
            )}
          </div>
        </div>
      </div>
    </li>
  );
}

interface ChatMessageProps {
  message: DisplayChatMessage;
  onRegenerate?: () => void;
  onRetry?: () => void;
}

function ChatMessageComponent({ message, onRegenerate, onRetry }: ChatMessageProps) {
  const assistant = message.role === "assistant";
  const fallback =
    message.status === "error"
      ? "回答生成失败。你可以重试这条消息。"
      : message.status === "stopped"
        ? "已停止生成。"
        : "";

  return (
    <article
      className={cn(
        "mx-auto flex w-full max-w-4xl gap-3 px-4 py-5 sm:gap-4 sm:px-6",
        !assistant && "justify-end",
      )}
      aria-label={assistant ? "助手消息" : "用户消息"}
    >
      {assistant && (
        <span className="grid size-8 shrink-0 place-items-center rounded-xl bg-primary text-white sm:size-9">
          <Bot className="size-4" aria-hidden="true" />
        </span>
      )}
      <div
        className={cn(
          "min-w-0",
          assistant
            ? "w-[calc(100%-2.75rem)]"
            : "max-w-[min(80%,42rem)] rounded-2xl rounded-br-md bg-[#e5f1ec] px-4 py-3",
        )}
      >
        {assistant ? (
          <>
            {message.content ? (
              <SafeMarkdown content={message.content} />
            ) : fallback ? (
              <p className="text-sm text-muted">{fallback}</p>
            ) : null}
            {message.status === "streaming" && (
              <p className="mt-2 inline-flex items-center gap-2 text-xs text-muted" role="status">
                <span className="size-1.5 animate-pulse rounded-full bg-primary" />
                正在生成回答
              </p>
            )}
            {message.citationError && (
              <p className="mt-4 rounded-xl border border-[#fedf89] bg-[#fffaeb] px-3 py-2 text-xs text-[#8a4506]">
                {message.citationError}
              </p>
            )}
            {message.citations?.length ? (
              <details className="mt-5 rounded-xl border bg-[#f8faf9] p-3 open:pb-4">
                <summary className="cursor-pointer text-xs font-semibold text-primary">
                  查看 {message.citations.length} 条引用来源
                </summary>
                <ol className="mt-3 space-y-2">
                  {message.citations.map((citation, index) => (
                    <CitationCard key={citation.id} citation={citation} index={index} />
                  ))}
                </ol>
              </details>
            ) : null}
            {(message.canRegenerate ||
              message.status === "error" ||
              message.status === "stopped") && (
              <div className="mt-3 flex flex-wrap gap-2">
                {message.canRegenerate && onRegenerate && (
                  <Button variant="ghost" size="sm" onClick={onRegenerate}>
                    <RefreshCcw className="size-3.5" aria-hidden="true" />
                    重新生成
                  </Button>
                )}
                {(message.status === "error" || message.status === "stopped") && onRetry && (
                  <Button variant="secondary" size="sm" onClick={onRetry}>
                    重试
                  </Button>
                )}
              </div>
            )}
          </>
        ) : (
          <p className="whitespace-pre-wrap break-words text-sm leading-6">{message.content}</p>
        )}
      </div>
      {!assistant && (
        <span className="grid size-8 shrink-0 place-items-center rounded-xl border bg-surface text-muted sm:size-9">
          <UserRound className="size-4" aria-hidden="true" />
        </span>
      )}
    </article>
  );
}

export const ChatMessage = memo(ChatMessageComponent);
