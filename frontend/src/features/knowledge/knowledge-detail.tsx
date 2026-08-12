import * as AlertDialog from "@radix-ui/react-alert-dialog";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Database, File, FileText, RefreshCcw, Trash2 } from "lucide-react";
import { useState } from "react";

import { ApiError } from "@/api/client";
import { deleteKnowledgeFile, getKnowledgeFiles } from "@/api/knowledge";
import { queryKeys } from "@/api/query-keys";
import type { KnowledgeBase, KnowledgeFile } from "@/api/types";
import { EmptyState } from "@/components/common/empty-state";
import { QueryError } from "@/components/common/query-error";
import { StatusMessage } from "@/components/common/status-message";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { FileUploader } from "@/features/knowledge/file-uploader";
import { formatDate, formatFileSize } from "@/utils/format";

interface KnowledgeDetailProps {
  knowledgeBase: KnowledgeBase;
  deletingKnowledgeBase: boolean;
  deleteKnowledgeBaseError?: string | null;
  onDeleteKnowledgeBase: () => void;
}

export function KnowledgeDetail({
  knowledgeBase,
  deletingKnowledgeBase,
  deleteKnowledgeBaseError,
  onDeleteKnowledgeBase,
}: KnowledgeDetailProps) {
  const queryClient = useQueryClient();
  const [deleteFileTarget, setDeleteFileTarget] = useState<KnowledgeFile | null>(null);
  const [deleteKnowledgeOpen, setDeleteKnowledgeOpen] = useState(false);
  const files = useQuery({
    queryKey: queryKeys.knowledge.files(knowledgeBase.id),
    queryFn: ({ signal }) => getKnowledgeFiles(knowledgeBase.id, signal),
    refetchInterval: (query) =>
      query.state.data?.files.some((file) => !file.is_processed) ? 5_000 : false,
  });
  const deleteFile = useMutation({
    mutationFn: (fileId: number) => deleteKnowledgeFile(knowledgeBase.id, fileId),
    onSuccess: () => {
      setDeleteFileTarget(null);
      void queryClient.invalidateQueries({ queryKey: queryKeys.knowledge.files(knowledgeBase.id) });
      void queryClient.invalidateQueries({ queryKey: ["knowledge"] });
    },
  });
  const deleteFileError = deleteFile.error
    ? deleteFile.error instanceof ApiError
      ? deleteFile.error.message
      : "文档删除失败，请重试"
    : null;

  return (
    <div className="min-w-0 space-y-5">
      <section className="rounded-2xl border bg-surface p-5 shadow-xs sm:p-6">
        <div className="flex flex-col gap-5 sm:flex-row sm:items-start">
          <span className="grid size-12 shrink-0 place-items-center rounded-2xl bg-[#eaf4f0] text-primary">
            <Database className="size-6" aria-hidden="true" />
          </span>
          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="break-words text-xl font-semibold">{knowledgeBase.name}</h2>
              <Badge tone={knowledgeBase.is_active ? "success" : "neutral"}>
                {knowledgeBase.is_active ? "可用" : "停用"}
              </Badge>
            </div>
            <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-muted">
              {knowledgeBase.description || "暂无描述"}
            </p>
            <div className="mt-4 flex flex-wrap gap-x-5 gap-y-2 text-xs text-muted">
              <span>{knowledgeBase.file_count} 个文件</span>
              <span>{knowledgeBase.document_count} 个文档块</span>
              <span>嵌入模型：{knowledgeBase.embedding_model}</span>
              <span>更新于 {formatDate(knowledgeBase.updated_at)}</span>
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            className="self-start text-danger"
            onClick={() => setDeleteKnowledgeOpen(true)}
          >
            <Trash2 className="size-3.5" aria-hidden="true" />
            删除知识库
          </Button>
        </div>
        {deleteKnowledgeBaseError && (
          <StatusMessage className="mt-4" tone="error">
            {deleteKnowledgeBaseError}
          </StatusMessage>
        )}
      </section>

      <FileUploader
        key={knowledgeBase.id}
        knowledgeBaseId={knowledgeBase.id}
        onUploaded={() => {
          void queryClient.invalidateQueries({
            queryKey: queryKeys.knowledge.files(knowledgeBase.id),
          });
          void queryClient.invalidateQueries({ queryKey: ["knowledge"] });
        }}
      />

      <section
        className="rounded-2xl border bg-surface shadow-xs"
        aria-labelledby="document-list-title"
      >
        <div className="flex items-center justify-between gap-3 border-b px-5 py-4 sm:px-6">
          <div>
            <h3 id="document-list-title" className="text-sm font-semibold">
              文档
            </h3>
            <p className="mt-1 text-xs text-muted">处理中的文档会每 5 秒自动刷新。</p>
          </div>
          <Button
            variant="ghost"
            size="icon"
            aria-label="刷新文档列表"
            onClick={() => void files.refetch()}
          >
            <RefreshCcw className="size-4" aria-hidden="true" />
          </Button>
        </div>
        <div className="p-4 sm:p-5">
          {deleteFileError && (
            <StatusMessage className="mb-4" tone="error">
              {deleteFileError}
            </StatusMessage>
          )}
          {files.isPending ? (
            <div className="space-y-3">
              {Array.from({ length: 3 }, (_, index) => (
                <Skeleton key={index} className="h-20 rounded-xl" />
              ))}
            </div>
          ) : files.isError ? (
            <QueryError message="文档列表加载失败" onRetry={() => void files.refetch()} />
          ) : files.data?.files.length ? (
            <ul className="space-y-3">
              {files.data.files.map((file) => (
                <li
                  key={file.id}
                  className="flex min-w-0 flex-col gap-3 rounded-xl border p-4 sm:flex-row sm:items-center"
                >
                  <span className="grid size-10 shrink-0 place-items-center rounded-xl bg-[#f2f4f7] text-[#475467]">
                    <FileText className="size-5" aria-hidden="true" />
                  </span>
                  <div className="min-w-0 flex-1">
                    <div className="flex min-w-0 flex-wrap items-center gap-2">
                      <p
                        className="max-w-full truncate text-sm font-medium"
                        title={file.original_filename}
                      >
                        {file.original_filename}
                      </p>
                      <Badge tone={file.is_processed ? "success" : "warning"}>
                        {file.is_processed ? "已完成" : "处理中"}
                      </Badge>
                    </div>
                    <p className="mt-1 text-xs text-muted">
                      {file.file_type?.toUpperCase() || "文件"} · {formatFileSize(file.file_size)} ·{" "}
                      {file.document_count} 个文档块 · {formatDate(file.updated_at)}
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="self-end text-danger sm:self-auto"
                    onClick={() => setDeleteFileTarget(file)}
                    aria-label={`删除文档：${file.original_filename}`}
                  >
                    <Trash2 className="size-4" aria-hidden="true" />
                  </Button>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState
              compact
              icon={File}
              title="还没有文档"
              description="上传第一个文件，完成后即可用于检索。"
            />
          )}
        </div>
      </section>

      <AlertDialog.Root
        open={Boolean(deleteFileTarget)}
        onOpenChange={(open) => !open && setDeleteFileTarget(null)}
      >
        <AlertDialog.Portal>
          <AlertDialog.Overlay className="fixed inset-0 z-50 bg-[#101828]/45 backdrop-blur-[2px]" />
          <AlertDialog.Content className="fixed left-1/2 top-1/2 z-50 w-[calc(100vw-24px)] max-w-md -translate-x-1/2 -translate-y-1/2 rounded-2xl border bg-surface p-6 shadow-2xl outline-none">
            <AlertDialog.Title className="text-lg font-semibold">删除这份文档？</AlertDialog.Title>
            <AlertDialog.Description className="mt-2 break-words text-sm leading-6 text-muted">
              “{deleteFileTarget?.original_filename}
              ”及其向量索引将从当前知识库移除，此操作不可撤销。
            </AlertDialog.Description>
            <div className="mt-6 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
              <AlertDialog.Cancel asChild>
                <Button variant="secondary">取消</Button>
              </AlertDialog.Cancel>
              <Button
                variant="destructive"
                disabled={deleteFile.isPending}
                onClick={() => deleteFileTarget && deleteFile.mutate(deleteFileTarget.id)}
              >
                确认删除
              </Button>
            </div>
          </AlertDialog.Content>
        </AlertDialog.Portal>
      </AlertDialog.Root>

      <AlertDialog.Root open={deleteKnowledgeOpen} onOpenChange={setDeleteKnowledgeOpen}>
        <AlertDialog.Portal>
          <AlertDialog.Overlay className="fixed inset-0 z-50 bg-[#101828]/45 backdrop-blur-[2px]" />
          <AlertDialog.Content className="fixed left-1/2 top-1/2 z-50 w-[calc(100vw-24px)] max-w-md -translate-x-1/2 -translate-y-1/2 rounded-2xl border bg-surface p-6 shadow-2xl outline-none">
            <AlertDialog.Title className="text-lg font-semibold">删除知识库？</AlertDialog.Title>
            <AlertDialog.Description className="mt-2 break-words text-sm leading-6 text-muted">
              “{knowledgeBase.name}”中的文件与向量索引都会被删除，相关 RAG
              对话将无法继续检索它。此操作不可撤销。
            </AlertDialog.Description>
            <div className="mt-6 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
              <AlertDialog.Cancel asChild>
                <Button variant="secondary">取消</Button>
              </AlertDialog.Cancel>
              <Button
                variant="destructive"
                disabled={deletingKnowledgeBase}
                onClick={() => {
                  onDeleteKnowledgeBase();
                  setDeleteKnowledgeOpen(false);
                }}
              >
                确认删除
              </Button>
            </div>
          </AlertDialog.Content>
        </AlertDialog.Portal>
      </AlertDialog.Root>
    </div>
  );
}
