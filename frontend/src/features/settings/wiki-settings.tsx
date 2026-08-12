import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { BookOpen, Globe2, HardDrive, RefreshCcw } from "lucide-react";

import { ApiError } from "@/api/client";
import { queryKeys } from "@/api/query-keys";
import { getWikiStatus, switchWikiMode } from "@/api/settings";
import { QueryError } from "@/components/common/query-error";
import { StatusMessage } from "@/components/common/status-message";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

export function WikiSettings() {
  const queryClient = useQueryClient();
  const wiki = useQuery({
    queryKey: queryKeys.settings.wiki,
    queryFn: ({ signal }) => getWikiStatus(signal),
    staleTime: 30_000,
  });
  const switchMode = useMutation({
    mutationFn: (mode: "online" | "offline") => switchWikiMode(mode),
    onSuccess: (response) => {
      queryClient.setQueryData(queryKeys.settings.wiki, response);
    },
  });
  const error = switchMode.error
    ? switchMode.error instanceof ApiError
      ? switchMode.error.message
      : "Wiki 模式切换失败"
    : null;

  return (
    <section className="rounded-2xl border bg-surface shadow-xs">
      <div className="flex items-start justify-between gap-4 border-b px-5 py-4 sm:px-6">
        <div>
          <h2 className="text-base font-semibold">Wiki 服务</h2>
          <p className="mt-1 text-xs leading-5 text-muted">查看服务状态并切换在线或离线检索。</p>
        </div>
        <Button
          variant="ghost"
          size="icon"
          aria-label="刷新 Wiki 状态"
          onClick={() => void wiki.refetch()}
        >
          <RefreshCcw className="size-4" aria-hidden="true" />
        </Button>
      </div>
      <div className="p-5 sm:p-6">
        {wiki.isPending ? (
          <div className="space-y-3">
            <Skeleton className="h-20" />
            <Skeleton className="h-11" />
          </div>
        ) : wiki.isError ? (
          <QueryError message="Wiki 状态读取失败" onRetry={() => void wiki.refetch()} />
        ) : (
          <>
            <div className="flex flex-col gap-4 rounded-xl border bg-[#fafbfb] p-4 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex items-center gap-3">
                <span className="grid size-10 place-items-center rounded-xl bg-[#eaf4f0] text-primary">
                  <BookOpen className="size-5" aria-hidden="true" />
                </span>
                <div>
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-semibold">维基百科知识</p>
                    <Badge tone={wiki.data?.success ? "success" : "danger"}>
                      {wiki.data?.success ? "可用" : "不可用"}
                    </Badge>
                  </div>
                  <p className="mt-1 text-xs text-muted">
                    当前模式：
                    {wiki.data?.mode === "online"
                      ? "在线"
                      : wiki.data?.mode === "offline"
                        ? "离线"
                        : "不可用"}
                    {wiki.data?.stats.total_articles
                      ? ` · ${wiki.data.stats.total_articles.toLocaleString("zh-CN")} 篇文章`
                      : ""}
                  </p>
                </div>
              </div>
              <div className="flex flex-wrap gap-2">
                <Button
                  type="button"
                  size="sm"
                  variant={wiki.data?.mode === "online" ? "default" : "secondary"}
                  disabled={switchMode.isPending}
                  onClick={() => switchMode.mutate("online")}
                >
                  <Globe2 className="size-3.5" aria-hidden="true" />
                  在线模式
                </Button>
                <Button
                  type="button"
                  size="sm"
                  variant={wiki.data?.mode === "offline" ? "default" : "secondary"}
                  disabled={switchMode.isPending}
                  onClick={() => switchMode.mutate("offline")}
                >
                  <HardDrive className="size-3.5" aria-hidden="true" />
                  离线模式
                </Button>
              </div>
            </div>
            {error && (
              <StatusMessage className="mt-4" tone="error">
                {error}
              </StatusMessage>
            )}
            {switchMode.isSuccess && (
              <StatusMessage className="mt-4" tone="success">
                Wiki 模式已更新
              </StatusMessage>
            )}
          </>
        )}
      </div>
    </section>
  );
}
