import { useQuery } from "@tanstack/react-query";
import { BookOpen, Database, Search } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { getKnowledgeBases } from "@/api/knowledge";
import { queryKeys } from "@/api/query-keys";
import { searchKnowledgeBase, searchWiki } from "@/api/search";
import { PageHeading } from "@/components/common/page-heading";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { SearchResults } from "@/features/search/search-results";
import type { SearchDisplayResult } from "@/features/search/types";
import { useDebouncedValue } from "@/hooks/use-debounced-value";
import { useAuthStore } from "@/stores/auth-store";
import { cn } from "@/utils/cn";

type SearchSource = "wiki" | "knowledge";

export function SearchWorkspace() {
  const userId = useAuthStore((state) => state.user?.user_id ?? 0);
  const [searchParams, setSearchParams] = useSearchParams();
  const initialSource = searchParams.get("source") === "knowledge" ? "knowledge" : "wiki";
  const initialKb = Number(searchParams.get("kb"));
  const initialQuery = searchParams.get("q") || "";
  const [source, setSource] = useState<SearchSource>(initialSource);
  const [knowledgeBaseId, setKnowledgeBaseId] = useState<number | null>(
    Number.isInteger(initialKb) && initialKb > 0 ? initialKb : null,
  );
  const [input, setInput] = useState(initialQuery);
  const [submittedQuery, setSubmittedQuery] = useState(initialQuery.trim());
  const debouncedInput = useDebouncedValue(input, 450);

  const knowledgeBases = useQuery({
    queryKey: queryKeys.knowledge.all(userId),
    queryFn: ({ signal }) => getKnowledgeBases(userId, { signal }),
    enabled: source === "knowledge" && Boolean(userId),
    staleTime: 30_000,
  });

  useEffect(() => {
    if (source !== "knowledge" || knowledgeBaseId || !knowledgeBases.data?.length) return;
    const first = knowledgeBases.data[0];
    if (first) setKnowledgeBaseId(first.id);
  }, [knowledgeBaseId, knowledgeBases.data, source]);

  const updateUrl = (query: string, replace = true) => {
    const next = new URLSearchParams();
    if (query) next.set("q", query);
    next.set("source", source);
    if (source === "knowledge" && knowledgeBaseId) next.set("kb", String(knowledgeBaseId));
    setSearchParams(next, { replace });
  };

  useEffect(() => {
    const query = debouncedInput.trim();
    if (query.length < 2 || query === submittedQuery) return;
    setSubmittedQuery(query);
    updateUrl(query);
    // updateUrl intentionally follows the current source and knowledge-base selection.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debouncedInput, knowledgeBaseId, source, submittedQuery]);

  const searchEnabled = Boolean(
    submittedQuery && (source === "wiki" || (source === "knowledge" && knowledgeBaseId)),
  );
  const search = useQuery({
    queryKey: queryKeys.search.results(source, knowledgeBaseId, submittedQuery),
    enabled: searchEnabled,
    staleTime: 60_000,
    queryFn: async ({ signal }): Promise<SearchDisplayResult[]> => {
      if (source === "wiki") {
        const response = await searchWiki(submittedQuery, { limit: 8, signal });
        return response.results.map((result, index) => ({
          id: `wiki-${index}-${result.title}`,
          title: result.title,
          content: result.content,
          source: response.mode === "offline" ? "维基百科（离线）" : "维基百科（在线）",
          kind: "wiki",
          score: result.score,
          url: result.url,
          categories: result.categories,
        }));
      }
      const response = await searchKnowledgeBase(knowledgeBaseId!, submittedQuery, {
        topK: 10,
        signal,
      });
      return response.results.map((result, index) => ({
        id: `knowledge-${knowledgeBaseId}-${index}`,
        title: result.source || response.knowledge_base_name,
        content: result.content,
        source: result.source || response.knowledge_base_name,
        kind: "knowledge",
        score: result.score,
        page: result.page,
        section: result.section,
      }));
    },
  });

  const sourceLabel = useMemo(() => {
    if (source === "wiki") return "Wiki";
    return knowledgeBases.data?.find(({ id }) => id === knowledgeBaseId)?.name || "所选知识库";
  }, [knowledgeBaseId, knowledgeBases.data, source]);

  const submit = () => {
    const query = input.trim();
    if (!query) {
      setSubmittedQuery("");
      updateUrl("");
      return;
    }
    setSubmittedQuery(query);
    updateUrl(query, false);
  };

  return (
    <div className="space-y-6">
      <PageHeading
        eyebrow="Search"
        title="知识搜索"
        description="在 Wiki 或指定知识库中执行结构化检索，并查看完整来源上下文。"
      />

      <section className="rounded-2xl border bg-surface p-4 shadow-xs sm:p-6" aria-label="搜索条件">
        <div className="flex flex-wrap gap-2" role="radiogroup" aria-label="搜索来源">
          <button
            type="button"
            role="radio"
            aria-checked={source === "wiki"}
            className={cn(
              "flex min-h-11 items-center gap-2 rounded-xl border px-4 text-sm font-medium",
              source === "wiki"
                ? "border-primary bg-[#eaf4f0] text-primary"
                : "bg-surface text-muted",
            )}
            onClick={() => setSource("wiki")}
          >
            <BookOpen className="size-4" aria-hidden="true" />
            Wiki 搜索
          </button>
          <button
            type="button"
            role="radio"
            aria-checked={source === "knowledge"}
            className={cn(
              "flex min-h-11 items-center gap-2 rounded-xl border px-4 text-sm font-medium",
              source === "knowledge"
                ? "border-primary bg-[#eaf4f0] text-primary"
                : "bg-surface text-muted",
            )}
            onClick={() => setSource("knowledge")}
          >
            <Database className="size-4" aria-hidden="true" />
            指定知识库
          </button>
        </div>

        {source === "knowledge" && (
          <div className="mt-4 max-w-md space-y-2">
            <Label htmlFor="search-knowledge-base">知识库</Label>
            {knowledgeBases.isPending ? (
              <Skeleton className="h-11" />
            ) : (
              <select
                id="search-knowledge-base"
                className="h-11 w-full rounded-xl border bg-surface px-3.5 text-sm outline-none focus-visible:border-primary focus-visible:ring-3 focus-visible:ring-primary/15"
                value={knowledgeBaseId ?? ""}
                onChange={(event) => setKnowledgeBaseId(Number(event.target.value) || null)}
              >
                <option value="">{knowledgeBases.isError ? "知识库加载失败" : "选择知识库"}</option>
                {knowledgeBases.data?.map((knowledgeBase) => (
                  <option key={knowledgeBase.id} value={knowledgeBase.id}>
                    {knowledgeBase.name}
                  </option>
                ))}
              </select>
            )}
            {knowledgeBases.isError && (
              <p className="text-xs text-danger">知识库列表加载失败，请刷新后重试。</p>
            )}
            {!knowledgeBases.isPending &&
              !knowledgeBases.isError &&
              !knowledgeBases.data?.length && (
                <p className="text-xs text-muted">还没有可搜索的知识库，请先上传文档。</p>
              )}
          </div>
        )}

        <form
          className="mt-5 flex min-w-0 flex-col gap-2 sm:flex-row"
          onSubmit={(event) => {
            event.preventDefault();
            submit();
          }}
        >
          <div className="min-w-0 flex-1">
            <Label htmlFor="search-query" className="sr-only">
              搜索关键词
            </Label>
            <Input
              id="search-query"
              type="search"
              value={input}
              placeholder={`搜索${sourceLabel}`}
              autoComplete="off"
              onChange={(event) => {
                setInput(event.target.value);
                if (!event.target.value.trim()) {
                  setSubmittedQuery("");
                  updateUrl("");
                }
              }}
            />
          </div>
          <Button
            type="submit"
            disabled={!input.trim() || (source === "knowledge" && !knowledgeBaseId)}
          >
            <Search className="size-4" aria-hidden="true" />
            立即搜索
          </Button>
        </form>
        <p className="mt-2 text-[11px] text-muted">
          输入停顿 450ms 后自动搜索；点击“立即搜索”或按 Enter 会马上执行。
        </p>
      </section>

      {submittedQuery && !search.isPending && !search.isError && (
        <p className="text-xs text-muted" aria-live="polite">
          在 {sourceLabel} 中找到 {search.data?.length ?? 0} 条与“{submittedQuery}”相关的结果
        </p>
      )}
      <SearchResults
        results={search.data || []}
        loading={search.isPending && searchEnabled}
        error={search.isError}
        searched={searchEnabled}
        onRetry={() => void search.refetch()}
      />
    </div>
  );
}
