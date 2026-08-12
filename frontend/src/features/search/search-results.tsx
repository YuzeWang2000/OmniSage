import { BookOpenText, FileSearch, SearchX } from "lucide-react";
import { useState } from "react";

import { EmptyState } from "@/components/common/empty-state";
import { QueryError } from "@/components/common/query-error";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { SearchResultDialog } from "@/features/search/search-result-dialog";
import type { SearchDisplayResult } from "@/features/search/types";

interface SearchResultsProps {
  results: SearchDisplayResult[];
  loading: boolean;
  error: boolean;
  searched: boolean;
  onRetry: () => void;
}

export function SearchResults({ results, loading, error, searched, onRetry }: SearchResultsProps) {
  const [selected, setSelected] = useState<SearchDisplayResult | null>(null);

  if (loading) {
    return (
      <div className="grid gap-4 lg:grid-cols-2">
        {Array.from({ length: 4 }, (_, index) => (
          <Skeleton key={index} className="h-48 rounded-2xl" />
        ))}
      </div>
    );
  }
  if (error) return <QueryError message="搜索失败，请检查检索服务后重试" onRetry={onRetry} />;
  if (!searched) {
    return (
      <EmptyState
        icon={FileSearch}
        title="搜索你的知识来源"
        description="输入关键词，选择 Wiki 或一个知识库后开始检索。"
      />
    );
  }
  if (!results.length) {
    return (
      <EmptyState
        icon={SearchX}
        title="没有找到相关内容"
        description="尝试更具体的关键词，或切换知识来源后重试。"
      />
    );
  }

  return (
    <>
      <ol className="grid gap-4 lg:grid-cols-2">
        {results.map((result, index) => (
          <li key={result.id}>
            <button
              type="button"
              className="flex h-full min-h-48 w-full min-w-0 flex-col rounded-2xl border bg-surface p-5 text-left shadow-xs transition-colors hover:border-[#b8d8cc] hover:bg-[#fbfdfc]"
              onClick={() => setSelected(result)}
              aria-label={`查看搜索结果：${result.title}`}
            >
              <div className="flex w-full min-w-0 items-start gap-3">
                <span className="grid size-8 shrink-0 place-items-center rounded-xl bg-[#eaf4f0] text-primary">
                  <BookOpenText className="size-4" aria-hidden="true" />
                </span>
                <div className="min-w-0 flex-1">
                  <div className="flex min-w-0 flex-wrap items-center gap-2">
                    <span className="text-xs font-semibold text-primary">
                      {String(index + 1).padStart(2, "0")}
                    </span>
                    <Badge>{result.kind === "wiki" ? "Wiki" : "知识库"}</Badge>
                    {result.score != null && (
                      <span className="text-[11px] text-muted">
                        相关度 {(Math.max(0, Math.min(1, result.score)) * 100).toFixed(1)}%
                      </span>
                    )}
                  </div>
                  <h3 className="mt-2 line-clamp-2 break-words text-sm font-semibold leading-6">
                    {result.title}
                  </h3>
                </div>
              </div>
              <p className="mt-3 line-clamp-4 whitespace-pre-wrap break-words text-xs leading-6 text-muted">
                {result.content}
              </p>
              <div className="mt-auto flex w-full flex-wrap gap-x-3 gap-y-1 pt-4 text-[11px] text-muted">
                <span className="max-w-full truncate">来源：{result.source}</span>
                {result.page != null && <span>第 {result.page} 页</span>}
                {result.section && <span className="max-w-full truncate">{result.section}</span>}
              </div>
            </button>
          </li>
        ))}
      </ol>
      <SearchResultDialog result={selected} onOpenChange={(open) => !open && setSelected(null)} />
    </>
  );
}
