import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Database, Plus } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { ApiError } from "@/api/client";
import {
  createKnowledgeBase,
  deleteKnowledgeBase as removeKnowledgeBase,
  getKnowledgeBases,
  updateKnowledgeBase,
} from "@/api/knowledge";
import { queryKeys } from "@/api/query-keys";
import type { KnowledgeBase } from "@/api/types";
import { EmptyState } from "@/components/common/empty-state";
import { PageHeading } from "@/components/common/page-heading";
import { Button } from "@/components/ui/button";
import {
  CreateKnowledgeDialog,
  type KnowledgeFormValues,
} from "@/features/knowledge/create-knowledge-dialog";
import { KnowledgeDetail } from "@/features/knowledge/knowledge-detail";
import { KnowledgeList } from "@/features/knowledge/knowledge-list";
import { useAuthStore } from "@/stores/auth-store";

function errorMessage(error: unknown, fallback: string) {
  return error instanceof ApiError ? error.message : fallback;
}

export function KnowledgeWorkspace() {
  const userId = useAuthStore((state) => state.user?.user_id ?? 0);
  const [searchParams, setSearchParams] = useSearchParams();
  const queryClient = useQueryClient();
  const [selectedId, setSelectedId] = useState<number | null>(() => {
    const requested = Number(searchParams.get("kb"));
    return Number.isInteger(requested) && requested > 0 ? requested : null;
  });
  const [createOpen, setCreateOpen] = useState(false);
  const knowledgeBases = useQuery({
    queryKey: queryKeys.knowledge.all(userId),
    queryFn: ({ signal }) => getKnowledgeBases(userId, { signal }),
    enabled: Boolean(userId),
  });

  const selectKnowledgeBase = useCallback(
    (id: number | null, replace = false) => {
      setSelectedId(id);
      const next = new URLSearchParams();
      if (id) next.set("kb", String(id));
      setSearchParams(next, { replace });
    },
    [setSearchParams],
  );

  useEffect(() => {
    if (!knowledgeBases.data) return;
    if (knowledgeBases.data.some(({ id }) => id === selectedId)) return;
    if (!knowledgeBases.data.length && selectedId === null) return;
    selectKnowledgeBase(knowledgeBases.data[0]?.id ?? null, true);
  }, [knowledgeBases.data, selectKnowledgeBase, selectedId]);

  const createKnowledge = useMutation({
    mutationFn: (values: KnowledgeFormValues) =>
      createKnowledgeBase({
        name: values.name,
        description: values.description || null,
        embedding_model: values.embeddingModel,
      }),
    onSuccess: (knowledgeBase) => {
      queryClient.setQueryData<KnowledgeBase[]>(queryKeys.knowledge.all(userId), (current = []) => [
        knowledgeBase,
        ...current,
      ]);
      setCreateOpen(false);
      selectKnowledgeBase(knowledgeBase.id);
      void queryClient.invalidateQueries({ queryKey: ["knowledge"] });
    },
  });
  const deleteKnowledge = useMutation({
    mutationFn: (id: number) => removeKnowledgeBase(id),
    onSuccess: (_, deletedId) => {
      const remaining = (knowledgeBases.data || []).filter(({ id }) => id !== deletedId);
      queryClient.setQueryData(queryKeys.knowledge.all(userId), remaining);
      queryClient.removeQueries({ queryKey: queryKeys.knowledge.files(deletedId) });
      selectKnowledgeBase(remaining[0]?.id ?? null, true);
      void queryClient.invalidateQueries({ queryKey: ["knowledge"] });
    },
  });
  const updateKnowledge = useMutation({
    mutationFn: ({ id, name, description }: { id: number; name: string; description: string | null }) =>
      updateKnowledgeBase(id, { name, description }),
    onSuccess: (updated) => {
      queryClient.setQueryData<KnowledgeBase[]>(queryKeys.knowledge.all(userId), (current = []) =>
        current.map((item) => item.id === updated.id ? updated : item),
      );
      void queryClient.invalidateQueries({ queryKey: ["knowledge"] });
    },
  });

  const selected = knowledgeBases.data?.find(({ id }) => id === selectedId);
  const createError = createKnowledge.error
    ? errorMessage(createKnowledge.error, "知识库创建失败，请重试")
    : null;
  const deleteError = deleteKnowledge.error
    ? errorMessage(deleteKnowledge.error, "知识库删除失败，请重试")
    : null;
  const updateError = updateKnowledge.error
    ? errorMessage(updateKnowledge.error, "知识库更新失败，请重试")
    : null;

  return (
    <div className="space-y-6">
      <PageHeading
        eyebrow="Knowledge"
        title="知识库"
        description="组织私有资料、跟踪索引状态，并为对话和搜索选择可信来源。"
        actions={
          <Button
            onClick={() => {
              createKnowledge.reset();
              setCreateOpen(true);
            }}
          >
            <Plus className="size-4" aria-hidden="true" />
            创建知识库
          </Button>
        }
      />

      <div className="grid min-w-0 gap-5 lg:grid-cols-[minmax(18rem,22rem)_minmax(0,1fr)]">
        <aside className="min-w-0" aria-label="知识库列表">
          <KnowledgeList
            items={knowledgeBases.data || []}
            activeId={selectedId}
            loading={knowledgeBases.isPending}
            error={knowledgeBases.isError}
            onRetry={() => void knowledgeBases.refetch()}
            onCreate={() => setCreateOpen(true)}
            onSelect={selectKnowledgeBase}
          />
        </aside>
        <main className="min-w-0">
          {selected ? (
            <KnowledgeDetail
              key={selected.id}
              knowledgeBase={selected}
              deletingKnowledgeBase={deleteKnowledge.isPending}
              deleteKnowledgeBaseError={deleteError}
              onDeleteKnowledgeBase={() => deleteKnowledge.mutate(selected.id)}
              updatingKnowledgeBase={updateKnowledge.isPending}
              updateKnowledgeBaseError={updateError}
              onUpdateKnowledgeBase={(name, description) =>
                updateKnowledge.mutateAsync({ id: selected.id, name, description })
              }
            />
          ) : knowledgeBases.isPending ? null : (
            <div className="rounded-2xl border bg-surface shadow-xs">
              <EmptyState
                icon={Database}
                title="选择一个知识库"
                description="选择后可查看详情、上传文档并管理索引。"
              />
            </div>
          )}
        </main>
      </div>

      <CreateKnowledgeDialog
        open={createOpen}
        pending={createKnowledge.isPending}
        error={createError}
        onOpenChange={setCreateOpen}
        onSubmit={(values) => createKnowledge.mutate(values)}
      />
    </div>
  );
}
