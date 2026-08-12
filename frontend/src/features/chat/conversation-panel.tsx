import * as AlertDialog from "@radix-ui/react-alert-dialog";
import * as Dialog from "@radix-ui/react-dialog";
import { MessageSquareText, Pencil, Plus, Trash2, X } from "lucide-react";
import { useEffect, useState } from "react";

import type { Conversation } from "@/api/types";
import { EmptyState } from "@/components/common/empty-state";
import { QueryError } from "@/components/common/query-error";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/utils/cn";
import { formatDate } from "@/utils/format";

interface ConversationPanelProps {
  conversations: Conversation[];
  activeId: number | null;
  loading: boolean;
  error: boolean;
  creating: boolean;
  mutating: boolean;
  onRetry: () => void;
  onCreate: () => void;
  onSelect: (id: number) => void;
  onRename: (id: number, title: string) => void;
  onDelete: (id: number) => void;
}

export function ConversationPanel({
  conversations,
  activeId,
  loading,
  error,
  creating,
  mutating,
  onRetry,
  onCreate,
  onSelect,
  onRename,
  onDelete,
}: ConversationPanelProps) {
  const [renameTarget, setRenameTarget] = useState<Conversation | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Conversation | null>(null);
  const [title, setTitle] = useState("");

  useEffect(() => setTitle(renameTarget?.title || ""), [renameTarget]);

  return (
    <div className="flex h-full min-h-0 flex-col bg-surface">
      <div className="border-b p-3">
        <Button className="w-full" onClick={onCreate} disabled={creating}>
          <Plus className="size-4" aria-hidden="true" />
          {creating ? "正在创建" : "新建对话"}
        </Button>
      </div>
      <div className="min-h-0 flex-1 overflow-y-auto p-2">
        {loading ? (
          <div className="space-y-2 p-1">
            {Array.from({ length: 6 }, (_, index) => (
              <Skeleton key={index} className="h-16 rounded-xl" />
            ))}
          </div>
        ) : error ? (
          <div className="p-2">
            <QueryError message="会话列表加载失败" onRetry={onRetry} />
          </div>
        ) : conversations.length ? (
          <ul className="space-y-1">
            {conversations.map((conversation) => (
              <li
                key={conversation.id}
                className={cn(
                  "group flex min-w-0 items-center gap-1 rounded-xl border border-transparent pr-1",
                  activeId === conversation.id
                    ? "border-[#c7ded5] bg-[#eaf4f0]"
                    : "hover:bg-[#f5f7f7]",
                )}
              >
                <button
                  type="button"
                  className="min-w-0 flex-1 px-3 py-2.5 text-left"
                  onClick={() => onSelect(conversation.id)}
                  aria-current={activeId === conversation.id ? "page" : undefined}
                  aria-label={`选择对话：${conversation.title}`}
                >
                  <span className="block truncate text-sm font-medium">{conversation.title}</span>
                  <span className="mt-1 block truncate text-[11px] text-muted">
                    {conversation.message_count} 条消息 · {formatDate(conversation.updated_at)}
                  </span>
                </button>
                <div className="flex shrink-0 opacity-100 xl:opacity-0 xl:group-hover:opacity-100 xl:group-focus-within:opacity-100">
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="size-8 min-h-8"
                    onClick={() => setRenameTarget(conversation)}
                    aria-label={`重命名对话：${conversation.title}`}
                  >
                    <Pencil className="size-3.5" aria-hidden="true" />
                  </Button>
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="size-8 min-h-8 text-danger"
                    onClick={() => setDeleteTarget(conversation)}
                    aria-label={`删除对话：${conversation.title}`}
                  >
                    <Trash2 className="size-3.5" aria-hidden="true" />
                  </Button>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <EmptyState
            compact
            icon={MessageSquareText}
            title="还没有对话"
            description="新建对话后会显示在这里。"
          />
        )}
      </div>

      <Dialog.Root
        open={Boolean(renameTarget)}
        onOpenChange={(open) => !open && setRenameTarget(null)}
      >
        <Dialog.Portal>
          <Dialog.Overlay className="fixed inset-0 z-50 bg-[#101828]/45 backdrop-blur-[2px]" />
          <Dialog.Content className="fixed left-1/2 top-1/2 z-50 w-[calc(100vw-24px)] max-w-md -translate-x-1/2 -translate-y-1/2 rounded-2xl border bg-surface p-5 shadow-2xl outline-none sm:p-6">
            <div className="flex items-start justify-between gap-4">
              <div>
                <Dialog.Title className="text-lg font-semibold">重命名对话</Dialog.Title>
                <Dialog.Description className="mt-1 text-sm text-muted">
                  标题最多保留 100 个字符。
                </Dialog.Description>
              </div>
              <Dialog.Close asChild>
                <Button variant="ghost" size="icon" aria-label="关闭重命名对话框">
                  <X className="size-4" />
                </Button>
              </Dialog.Close>
            </div>
            <form
              className="mt-5 space-y-4"
              onSubmit={(event) => {
                event.preventDefault();
                if (!renameTarget || !title.trim()) return;
                onRename(renameTarget.id, title.trim());
                setRenameTarget(null);
              }}
            >
              <div className="space-y-2">
                <Label htmlFor="conversation-title">对话标题</Label>
                <Input
                  id="conversation-title"
                  value={title}
                  maxLength={100}
                  autoFocus
                  onChange={(event) => setTitle(event.target.value)}
                />
              </div>
              <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
                <Dialog.Close asChild>
                  <Button type="button" variant="secondary">
                    取消
                  </Button>
                </Dialog.Close>
                <Button type="submit" disabled={!title.trim() || mutating}>
                  保存标题
                </Button>
              </div>
            </form>
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>

      <AlertDialog.Root
        open={Boolean(deleteTarget)}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
      >
        <AlertDialog.Portal>
          <AlertDialog.Overlay className="fixed inset-0 z-50 bg-[#101828]/45 backdrop-blur-[2px]" />
          <AlertDialog.Content className="fixed left-1/2 top-1/2 z-50 w-[calc(100vw-24px)] max-w-md -translate-x-1/2 -translate-y-1/2 rounded-2xl border bg-surface p-6 shadow-2xl outline-none">
            <AlertDialog.Title className="text-lg font-semibold">删除这段对话？</AlertDialog.Title>
            <AlertDialog.Description className="mt-2 text-sm leading-6 text-muted">
              “{deleteTarget?.title}”及其历史消息将被删除，此操作不可撤销。
            </AlertDialog.Description>
            <div className="mt-6 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
              <AlertDialog.Cancel asChild>
                <Button variant="secondary">取消</Button>
              </AlertDialog.Cancel>
              <Button
                variant="destructive"
                disabled={mutating}
                onClick={() => {
                  if (!deleteTarget) return;
                  onDelete(deleteTarget.id);
                  setDeleteTarget(null);
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
