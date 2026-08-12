import { Database, FileText, Plus } from "lucide-react";

import type { KnowledgeBase } from "@/api/types";
import { EmptyState } from "@/components/common/empty-state";
import { QueryError } from "@/components/common/query-error";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/utils/cn";

interface KnowledgeListProps {
  items: KnowledgeBase[];
  activeId: number | null;
  loading: boolean;
  error: boolean;
  onRetry: () => void;
  onCreate: () => void;
  onSelect: (id: number) => void;
}

export function KnowledgeList({
  items,
  activeId,
  loading,
  error,
  onRetry,
  onCreate,
  onSelect,
}: KnowledgeListProps) {
  if (loading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 4 }, (_, index) => (
          <Skeleton key={index} className="h-28 rounded-2xl" />
        ))}
      </div>
    );
  }
  if (error) return <QueryError message="知识库列表加载失败" onRetry={onRetry} />;
  if (!items.length) {
    return (
      <EmptyState
        icon={Database}
        title="还没有知识库"
        description="创建知识库并上传资料后，即可用于搜索和 RAG 问答。"
        action={
          <Button onClick={onCreate}>
            <Plus className="size-4" />
            创建知识库
          </Button>
        }
      />
    );
  }

  return (
    <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-1">
      {items.map((knowledgeBase) => (
        <li key={knowledgeBase.id}>
          <button
            type="button"
            className={cn(
              "w-full rounded-2xl border bg-surface p-4 text-left shadow-xs transition-colors hover:bg-[#f8faf9]",
              activeId === knowledgeBase.id &&
                "border-[#9cc9b9] bg-[#eef7f3] ring-2 ring-primary/10",
            )}
            onClick={() => onSelect(knowledgeBase.id)}
            aria-current={activeId === knowledgeBase.id ? "page" : undefined}
            aria-label={`查看知识库：${knowledgeBase.name}`}
          >
            <div className="flex min-w-0 items-start gap-3">
              <span className="grid size-9 shrink-0 place-items-center rounded-xl bg-[#eaf4f0] text-primary">
                <Database className="size-4" aria-hidden="true" />
              </span>
              <span className="min-w-0 flex-1">
                <span className="block truncate text-sm font-semibold">{knowledgeBase.name}</span>
                <span className="mt-1 line-clamp-2 block min-h-10 text-xs leading-5 text-muted">
                  {knowledgeBase.description || "暂无描述"}
                </span>
              </span>
            </div>
            <span className="mt-3 flex items-center gap-4 text-[11px] text-muted">
              <span className="inline-flex items-center gap-1">
                <FileText className="size-3" />
                {knowledgeBase.file_count} 个文件
              </span>
              <span>{knowledgeBase.document_count} 个文档块</span>
            </span>
          </button>
        </li>
      ))}
    </ul>
  );
}
