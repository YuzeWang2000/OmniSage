import * as Dialog from "@radix-ui/react-dialog";
import { zodResolver } from "@hookform/resolvers/zod";
import { LoaderCircle, X } from "lucide-react";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const knowledgeSchema = z.object({
  name: z.string().trim().min(1, "请输入知识库名称").max(100, "名称不能超过 100 个字符"),
  description: z.string().trim().max(500, "描述不能超过 500 个字符"),
  embeddingModel: z.string().min(1),
});

export type KnowledgeFormValues = z.infer<typeof knowledgeSchema>;

interface CreateKnowledgeDialogProps {
  open: boolean;
  pending: boolean;
  error?: string | null;
  onOpenChange: (open: boolean) => void;
  onSubmit: (values: KnowledgeFormValues) => void;
}

export function CreateKnowledgeDialog({
  open,
  pending,
  error,
  onOpenChange,
  onSubmit,
}: CreateKnowledgeDialogProps) {
  const form = useForm<KnowledgeFormValues>({
    resolver: zodResolver(knowledgeSchema),
    defaultValues: { name: "", description: "", embeddingModel: "nomic-embed-text" },
  });

  useEffect(() => {
    if (!open) form.reset();
  }, [form, open]);

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-50 bg-[#101828]/45 backdrop-blur-[2px]" />
        <Dialog.Content className="fixed inset-y-3 left-1/2 z-50 w-[calc(100vw-24px)] max-w-lg -translate-x-1/2 overflow-y-auto rounded-2xl border bg-surface p-5 shadow-2xl outline-none sm:inset-y-auto sm:top-1/2 sm:max-h-[calc(100vh-24px)] sm:-translate-y-1/2 sm:p-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <Dialog.Title className="text-lg font-semibold">创建知识库</Dialog.Title>
              <Dialog.Description className="mt-1 text-sm leading-6 text-muted">
                创建独立的文档集合，用于检索和 RAG 问答。
              </Dialog.Description>
            </div>
            <Dialog.Close asChild>
              <Button variant="ghost" size="icon" aria-label="关闭创建知识库表单">
                <X className="size-4" />
              </Button>
            </Dialog.Close>
          </div>
          <form className="mt-6 space-y-4" onSubmit={form.handleSubmit(onSubmit)}>
            <div className="space-y-2">
              <Label htmlFor="knowledge-name">名称</Label>
              <Input
                id="knowledge-name"
                autoFocus
                maxLength={100}
                aria-invalid={Boolean(form.formState.errors.name)}
                {...form.register("name")}
              />
              {form.formState.errors.name && (
                <p className="text-xs text-danger">{form.formState.errors.name.message}</p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="knowledge-description">描述（可选）</Label>
              <textarea
                id="knowledge-description"
                rows={4}
                maxLength={500}
                className="w-full resize-y rounded-xl border bg-surface px-3.5 py-3 text-sm outline-none focus-visible:border-primary focus-visible:ring-3 focus-visible:ring-primary/15"
                placeholder="说明这个知识库的内容与用途"
                {...form.register("description")}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="embedding-model">嵌入模型</Label>
              <select
                id="embedding-model"
                className="h-11 w-full rounded-xl border bg-surface px-3.5 text-sm outline-none focus-visible:border-primary focus-visible:ring-3 focus-visible:ring-primary/15"
                {...form.register("embeddingModel")}
              >
                <option value="nomic-embed-text">nomic-embed-text</option>
              </select>
              <p className="text-xs leading-5 text-muted">
                上传前请确认后端 Ollama 已安装该嵌入模型。
              </p>
            </div>
            {error && (
              <p
                className="rounded-xl border border-[#fecdca] bg-[#fef3f2] px-3 py-2 text-sm text-danger"
                role="alert"
              >
                {error}
              </p>
            )}
            <div className="flex flex-col-reverse gap-2 pt-2 sm:flex-row sm:justify-end">
              <Dialog.Close asChild>
                <Button type="button" variant="secondary">
                  取消
                </Button>
              </Dialog.Close>
              <Button type="submit" disabled={pending}>
                {pending && <LoaderCircle className="size-4 animate-spin" />}
                {pending ? "正在创建" : "创建知识库"}
              </Button>
            </div>
          </form>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
