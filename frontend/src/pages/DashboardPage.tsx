import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ArrowRight,
  Database,
  FileText,
  MessageSquareText,
  Plus,
  Search,
  Sparkles,
} from "lucide-react";
import { Link, useNavigate } from "react-router-dom";

import { createConversation, getConversations } from "@/api/conversations";
import { getKnowledgeBases, getKnowledgeStats } from "@/api/knowledge";
import { queryKeys } from "@/api/query-keys";
import { ApiError } from "@/api/client";
import { EmptyState } from "@/components/common/empty-state";
import { PageHeading } from "@/components/common/page-heading";
import { QueryError } from "@/components/common/query-error";
import { StatusMessage } from "@/components/common/status-message";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuthStore } from "@/stores/auth-store";
import { useChatStore } from "@/stores/chat-store";
import { formatDate } from "@/utils/format";

const metricCards = [
  { key: "total_knowledge_bases", label: "知识库", icon: Database },
  { key: "total_files", label: "已上传文件", icon: FileText },
  { key: "total_documents", label: "文档块", icon: Sparkles },
] as const;

export default function DashboardPage() {
  const user = useAuthStore((state) => state.user);
  const setActiveConversationId = useChatStore((state) => state.setActiveConversationId);
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const userId = user?.user_id ?? 0;

  const recentConversations = useQuery({
    queryKey: queryKeys.conversations.recent(userId),
    queryFn: ({ signal }) => getConversations(userId, { limit: 5, signal }),
    enabled: Boolean(userId),
  });
  const recentKnowledge = useQuery({
    queryKey: queryKeys.knowledge.recent(userId),
    queryFn: ({ signal }) => getKnowledgeBases(userId, { limit: 4, signal }),
    enabled: Boolean(userId),
  });
  const stats = useQuery({
    queryKey: queryKeys.knowledge.stats(userId),
    queryFn: ({ signal }) => getKnowledgeStats(userId, signal),
    enabled: Boolean(userId),
  });
  const newConversation = useMutation({
    mutationFn: () => createConversation(),
    onSuccess: (conversation) => {
      setActiveConversationId(conversation.id);
      void queryClient.invalidateQueries({ queryKey: ["conversations", userId] });
      navigate(`/chat?conversation=${conversation.id}`);
    },
  });

  const mutationError = newConversation.error
    ? newConversation.error instanceof ApiError
      ? newConversation.error.message
      : "新建对话失败"
    : null;

  return (
    <div className="space-y-6 sm:space-y-8">
      <PageHeading
        eyebrow="Overview"
        title={`你好，${user?.username || "用户"}`}
        description="继续最近的知识工作，或从一个新问题开始。"
        actions={
          <Button onClick={() => newConversation.mutate()} disabled={newConversation.isPending}>
            <Plus className="size-4" aria-hidden="true" />
            {newConversation.isPending ? "正在创建" : "新建对话"}
          </Button>
        }
      />

      {mutationError && <StatusMessage tone="error">{mutationError}</StatusMessage>}

      <section aria-label="知识库概览" className="grid gap-3 sm:grid-cols-3">
        {stats.isPending ? (
          Array.from({ length: 3 }, (_, index) => (
            <Skeleton key={index} className="h-28 rounded-2xl" />
          ))
        ) : stats.isError ? (
          <div className="sm:col-span-3">
            <QueryError message="知识库概览加载失败" onRetry={() => void stats.refetch()} />
          </div>
        ) : (
          metricCards.map(({ key, label, icon: Icon }) => (
            <article key={key} className="rounded-2xl border bg-surface p-5 shadow-xs">
              <div className="flex items-center justify-between gap-3">
                <p className="text-sm text-muted">{label}</p>
                <Icon className="size-4 text-primary" aria-hidden="true" />
              </div>
              <p className="mt-4 text-3xl font-semibold tracking-tight">
                {stats.data?.[key].toLocaleString("zh-CN") ?? 0}
              </p>
            </article>
          ))
        )}
      </section>

      <section aria-label="快捷操作" className="grid gap-3 md:grid-cols-3">
        <button
          type="button"
          className="group flex min-h-24 items-center gap-4 rounded-2xl border bg-[#eaf4f0] p-5 text-left transition-colors hover:border-[#afd4c6]"
          onClick={() => newConversation.mutate()}
        >
          <span className="grid size-10 shrink-0 place-items-center rounded-xl bg-primary text-white">
            <MessageSquareText className="size-5" aria-hidden="true" />
          </span>
          <span className="min-w-0">
            <span className="block text-sm font-semibold">提出新问题</span>
            <span className="mt-1 block text-xs leading-5 text-muted">创建空白会话并开始问答</span>
          </span>
          <ArrowRight className="ml-auto size-4 shrink-0 text-primary" aria-hidden="true" />
        </button>
        <Link
          to="/knowledge"
          className="group flex min-h-24 items-center gap-4 rounded-2xl border bg-surface p-5 transition-colors hover:bg-[#f8faf9]"
        >
          <span className="grid size-10 shrink-0 place-items-center rounded-xl bg-[#f2f4f7] text-[#344054]">
            <Database className="size-5" aria-hidden="true" />
          </span>
          <span className="min-w-0">
            <span className="block text-sm font-semibold">管理知识库</span>
            <span className="mt-1 block text-xs leading-5 text-muted">上传并组织知识资料</span>
          </span>
          <ArrowRight className="ml-auto size-4 shrink-0 text-muted" aria-hidden="true" />
        </Link>
        <Link
          to="/search"
          className="group flex min-h-24 items-center gap-4 rounded-2xl border bg-surface p-5 transition-colors hover:bg-[#f8faf9]"
        >
          <span className="grid size-10 shrink-0 place-items-center rounded-xl bg-[#f2f4f7] text-[#344054]">
            <Search className="size-5" aria-hidden="true" />
          </span>
          <span className="min-w-0">
            <span className="block text-sm font-semibold">搜索知识</span>
            <span className="mt-1 block text-xs leading-5 text-muted">精确检索 Wiki 或文档</span>
          </span>
          <ArrowRight className="ml-auto size-4 shrink-0 text-muted" aria-hidden="true" />
        </Link>
      </section>

      <div className="grid min-w-0 gap-5 xl:grid-cols-2">
        <section className="min-w-0 rounded-2xl border bg-surface shadow-xs">
          <div className="flex items-center justify-between border-b px-5 py-4">
            <div>
              <h2 className="text-sm font-semibold">最近对话</h2>
              <p className="mt-0.5 text-xs text-muted">仅加载最近 5 条</p>
            </div>
            <Link to="/chat" className="text-xs font-medium text-primary hover:underline">
              查看全部
            </Link>
          </div>
          {recentConversations.isPending ? (
            <div className="space-y-3 p-5">
              {Array.from({ length: 3 }, (_, index) => (
                <Skeleton key={index} className="h-14" />
              ))}
            </div>
          ) : recentConversations.isError ? (
            <div className="p-5">
              <QueryError
                message="最近对话加载失败"
                onRetry={() => void recentConversations.refetch()}
              />
            </div>
          ) : recentConversations.data?.length ? (
            <ul className="divide-y">
              {recentConversations.data.map((conversation) => (
                <li key={conversation.id}>
                  <Link
                    to={`/chat?conversation=${conversation.id}`}
                    onClick={() => setActiveConversationId(conversation.id)}
                    className="flex min-h-16 items-center gap-3 px-5 py-3 hover:bg-[#f8faf9]"
                  >
                    <span className="grid size-9 shrink-0 place-items-center rounded-xl bg-[#eef2f1] text-primary">
                      <MessageSquareText className="size-4" aria-hidden="true" />
                    </span>
                    <span className="min-w-0 flex-1">
                      <span className="block truncate text-sm font-medium">
                        {conversation.title}
                      </span>
                      <span className="mt-0.5 block text-xs text-muted">
                        {conversation.message_count} 条消息 · {formatDate(conversation.updated_at)}
                      </span>
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState
              compact
              icon={MessageSquareText}
              title="还没有对话"
              description="从一个问题开始，首条消息会自动生成标题。"
            />
          )}
        </section>

        <section className="min-w-0 rounded-2xl border bg-surface shadow-xs">
          <div className="flex items-center justify-between border-b px-5 py-4">
            <div>
              <h2 className="text-sm font-semibold">知识库</h2>
              <p className="mt-0.5 text-xs text-muted">最近更新的 4 个知识库</p>
            </div>
            <Link to="/knowledge" className="text-xs font-medium text-primary hover:underline">
              管理
            </Link>
          </div>
          {recentKnowledge.isPending ? (
            <div className="grid gap-3 p-5 sm:grid-cols-2">
              {Array.from({ length: 4 }, (_, index) => (
                <Skeleton key={index} className="h-24" />
              ))}
            </div>
          ) : recentKnowledge.isError ? (
            <div className="p-5">
              <QueryError
                message="知识库列表加载失败"
                onRetry={() => void recentKnowledge.refetch()}
              />
            </div>
          ) : recentKnowledge.data?.length ? (
            <div className="grid gap-3 p-4 sm:grid-cols-2">
              {recentKnowledge.data.map((knowledgeBase) => (
                <Link
                  key={knowledgeBase.id}
                  to={`/knowledge?kb=${knowledgeBase.id}`}
                  className="min-w-0 rounded-xl border p-4 hover:bg-[#f8faf9]"
                >
                  <p className="truncate text-sm font-medium">{knowledgeBase.name}</p>
                  <p className="mt-1 line-clamp-2 min-h-10 text-xs leading-5 text-muted">
                    {knowledgeBase.description || "暂无描述"}
                  </p>
                  <p className="mt-3 text-[11px] text-muted">
                    {knowledgeBase.file_count} 个文件 · {knowledgeBase.document_count} 个文档块
                  </p>
                </Link>
              ))}
            </div>
          ) : (
            <EmptyState
              compact
              icon={Database}
              title="还没有知识库"
              description="创建知识库后，可以上传文档用于 RAG 问答。"
            />
          )}
        </section>
      </div>
    </div>
  );
}
