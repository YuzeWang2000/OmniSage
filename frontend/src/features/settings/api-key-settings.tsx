import * as AlertDialog from "@radix-ui/react-alert-dialog";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { KeyRound, Pencil, Plus, Trash2 } from "lucide-react";
import { useState } from "react";

import { ApiError } from "@/api/client";
import { queryKeys } from "@/api/query-keys";
import { createApiKey, deleteApiKey, getApiKeys, updateApiKey } from "@/api/settings";
import type { ApiKey } from "@/api/types";
import { EmptyState } from "@/components/common/empty-state";
import { QueryError } from "@/components/common/query-error";
import { StatusMessage } from "@/components/common/status-message";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ApiKeyDialog, type ApiKeyFormValues } from "@/features/settings/api-key-dialog";
import { useAuthStore } from "@/stores/auth-store";
import { maskApiKey } from "@/utils/api-key";
import { formatDate } from "@/utils/format";

export function ApiKeySettings() {
  const userId = useAuthStore((state) => state.user?.user_id ?? 0);
  const queryClient = useQueryClient();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<ApiKey | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<ApiKey | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const apiKeys = useQuery({
    queryKey: queryKeys.settings.apiKeys(userId),
    queryFn: ({ signal }) => getApiKeys(userId, signal),
    enabled: Boolean(userId),
  });
  const saveKey = useMutation({
    mutationFn: (values: ApiKeyFormValues) =>
      editing
        ? updateApiKey(editing.id, {
            api_key: values.apiKey,
            model_name: values.modelName || null,
            is_active: values.isActive,
          })
        : createApiKey({
            provider: values.provider,
            api_key: values.apiKey,
            model_name: values.modelName || null,
          }),
    onSuccess: () => {
      setSuccess(editing ? "API Key 已更新" : "API Key 已添加");
      setDialogOpen(false);
      setEditing(null);
      void queryClient.invalidateQueries({ queryKey: queryKeys.settings.apiKeys(userId) });
    },
  });
  const removeKey = useMutation({
    mutationFn: (id: number) => deleteApiKey(id),
    onSuccess: () => {
      setSuccess("API Key 已删除");
      setDeleteTarget(null);
      void queryClient.invalidateQueries({ queryKey: queryKeys.settings.apiKeys(userId) });
    },
  });

  const mutationError = saveKey.error || removeKey.error;
  const errorMessage = mutationError
    ? mutationError instanceof ApiError
      ? mutationError.message
      : "API Key 操作失败"
    : null;

  const openCreate = () => {
    setEditing(null);
    saveKey.reset();
    setDialogOpen(true);
  };
  const openEdit = (key: ApiKey) => {
    setEditing(key);
    saveKey.reset();
    setDialogOpen(true);
  };

  return (
    <section className="rounded-2xl border bg-surface shadow-xs">
      <div className="flex items-start justify-between gap-4 border-b px-5 py-4 sm:px-6">
        <div>
          <h2 className="text-base font-semibold">API Key</h2>
          <p className="mt-1 text-xs leading-5 text-muted">
            为在线模型配置独立密钥，保存后仅显示掩码。
          </p>
        </div>
        <Button size="sm" onClick={openCreate}>
          <Plus className="size-3.5" aria-hidden="true" />
          添加
        </Button>
      </div>
      <div className="p-5 sm:p-6">
        {success && (
          <StatusMessage className="mb-4" tone="success">
            {success}
          </StatusMessage>
        )}
        {errorMessage && (
          <StatusMessage className="mb-4" tone="error">
            {errorMessage}
          </StatusMessage>
        )}
        {apiKeys.isPending ? (
          <div className="space-y-3">
            {Array.from({ length: 2 }, (_, index) => (
              <Skeleton key={index} className="h-20" />
            ))}
          </div>
        ) : apiKeys.isError ? (
          <QueryError message="API Key 列表读取失败" onRetry={() => void apiKeys.refetch()} />
        ) : apiKeys.data?.length ? (
          <ul className="space-y-3">
            {apiKeys.data.map((key) => (
              <li
                key={key.id}
                className="flex flex-col gap-4 rounded-xl border p-4 sm:flex-row sm:items-center"
              >
                <span className="grid size-10 shrink-0 place-items-center rounded-xl bg-[#eef2f1] text-primary">
                  <KeyRound className="size-5" aria-hidden="true" />
                </span>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <p className="text-sm font-semibold capitalize">{key.provider}</p>
                    <Badge tone={key.is_active ? "success" : "neutral"}>
                      {key.is_active ? "已启用" : "已停用"}
                    </Badge>
                  </div>
                  <p
                    className="mt-1 font-mono text-xs tracking-wide text-muted"
                    aria-label={`${key.provider} 密钥已掩码`}
                  >
                    {maskApiKey()}
                  </p>
                  <p className="mt-1 text-[11px] text-muted">
                    {key.model_name || "未指定模型"} · 更新于 {formatDate(key.updated_at)}
                  </p>
                </div>
                <div className="flex gap-2 sm:shrink-0">
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => openEdit(key)}
                    aria-label={`更新 ${key.provider} API Key`}
                  >
                    <Pencil className="size-3.5" aria-hidden="true" />
                    更新
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="size-9 min-h-9 text-danger"
                    onClick={() => setDeleteTarget(key)}
                    aria-label={`删除 ${key.provider} API Key`}
                  >
                    <Trash2 className="size-4" aria-hidden="true" />
                  </Button>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <EmptyState
            compact
            icon={KeyRound}
            title="还没有 API Key"
            description="本地模型无需密钥；使用在线模型时再添加。"
            action={
              <Button size="sm" onClick={openCreate}>
                添加第一个密钥
              </Button>
            }
          />
        )}
      </div>

      <ApiKeyDialog
        open={dialogOpen}
        editing={editing}
        pending={saveKey.isPending}
        onOpenChange={(open) => {
          setDialogOpen(open);
          if (!open) setEditing(null);
        }}
        onSubmit={(values) => saveKey.mutate(values)}
      />

      <AlertDialog.Root
        open={Boolean(deleteTarget)}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
      >
        <AlertDialog.Portal>
          <AlertDialog.Overlay className="fixed inset-0 z-50 bg-[#101828]/45 backdrop-blur-[2px]" />
          <AlertDialog.Content className="fixed left-1/2 top-1/2 z-50 w-[calc(100vw-24px)] max-w-md -translate-x-1/2 -translate-y-1/2 rounded-2xl border bg-surface p-6 shadow-2xl outline-none">
            <AlertDialog.Title className="text-lg font-semibold">删除 API Key？</AlertDialog.Title>
            <AlertDialog.Description className="mt-2 text-sm leading-6 text-muted">
              删除后，使用 {deleteTarget?.provider} 在线模型的请求可能无法继续。此操作不可撤销。
            </AlertDialog.Description>
            <div className="mt-6 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
              <AlertDialog.Cancel asChild>
                <Button variant="secondary">取消</Button>
              </AlertDialog.Cancel>
              <Button
                variant="destructive"
                disabled={removeKey.isPending}
                onClick={() => deleteTarget && removeKey.mutate(deleteTarget.id)}
              >
                确认删除
              </Button>
            </div>
          </AlertDialog.Content>
        </AlertDialog.Portal>
      </AlertDialog.Root>
    </section>
  );
}
