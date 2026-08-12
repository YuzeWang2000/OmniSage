import * as Dialog from "@radix-ui/react-dialog";
import { zodResolver } from "@hookform/resolvers/zod";
import { LoaderCircle, X } from "lucide-react";
import { Controller, useForm } from "react-hook-form";
import { z } from "zod";

import type { ApiKey } from "@/api/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";

const apiKeySchema = z.object({
  provider: z.string().min(1, "请选择提供商"),
  apiKey: z.string().trim().min(1, "请输入 API Key"),
  modelName: z.string(),
  isActive: z.boolean(),
});

export type ApiKeyFormValues = z.infer<typeof apiKeySchema>;

interface ApiKeyDialogProps {
  open: boolean;
  editing?: ApiKey | null;
  pending: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (values: ApiKeyFormValues) => void;
}

export function ApiKeyDialog({
  open,
  editing,
  pending,
  onOpenChange,
  onSubmit,
}: ApiKeyDialogProps) {
  const form = useForm<ApiKeyFormValues>({
    resolver: zodResolver(apiKeySchema),
    values: {
      provider: editing?.provider || "deepseek",
      apiKey: "",
      modelName: editing?.model_name || "",
      isActive: editing?.is_active ?? true,
    },
  });

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-50 bg-[#101828]/45 backdrop-blur-[2px]" />
        <Dialog.Content className="fixed left-1/2 top-1/2 z-50 max-h-[calc(100vh-24px)] w-[calc(100vw-24px)] max-w-lg -translate-x-1/2 -translate-y-1/2 overflow-y-auto rounded-2xl border bg-surface p-5 shadow-2xl outline-none sm:p-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <Dialog.Title className="text-lg font-semibold">
                {editing ? "更新 API Key" : "添加 API Key"}
              </Dialog.Title>
              <Dialog.Description className="mt-1 text-xs leading-5 text-muted">
                密钥只会发送到 OmniSage FastAPI，不会在保存后完整回显。
              </Dialog.Description>
            </div>
            <Dialog.Close asChild>
              <Button variant="ghost" size="icon" aria-label="关闭 API Key 表单">
                <X className="size-4" aria-hidden="true" />
              </Button>
            </Dialog.Close>
          </div>

          <form className="mt-6 space-y-4" onSubmit={form.handleSubmit(onSubmit)}>
            <div className="space-y-2">
              <Label htmlFor="api-provider">提供商</Label>
              <select
                id="api-provider"
                className="h-11 w-full rounded-xl border bg-surface px-3.5 text-sm outline-none focus-visible:border-primary focus-visible:ring-3 focus-visible:ring-primary/15 disabled:bg-[#f2f4f7]"
                disabled={Boolean(editing)}
                {...form.register("provider")}
              >
                <option value="deepseek">DeepSeek</option>
                <option value="openai">OpenAI</option>
                <option value="anthropic">Anthropic</option>
                <option value="google">Google</option>
              </select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="api-key-value">{editing ? "新的 API Key" : "API Key"}</Label>
              <Input
                id="api-key-value"
                type="password"
                autoComplete="off"
                spellCheck={false}
                placeholder={editing ? "输入新密钥以替换现有密钥" : "输入密钥"}
                aria-invalid={Boolean(form.formState.errors.apiKey)}
                {...form.register("apiKey")}
              />
              {form.formState.errors.apiKey && (
                <p className="text-xs text-danger">{form.formState.errors.apiKey.message}</p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="api-model">模型名称（可选）</Label>
              <Input
                id="api-model"
                placeholder="例如 deepseek-chat"
                {...form.register("modelName")}
              />
            </div>
            {editing && (
              <Controller
                name="isActive"
                control={form.control}
                render={({ field }) => (
                  <div className="flex items-center justify-between rounded-xl border p-4">
                    <Label htmlFor="api-active">启用此密钥</Label>
                    <Switch
                      id="api-active"
                      checked={field.value}
                      onCheckedChange={field.onChange}
                    />
                  </div>
                )}
              />
            )}
            <div className="flex flex-col-reverse gap-2 pt-2 sm:flex-row sm:justify-end">
              <Button type="button" variant="secondary" onClick={() => onOpenChange(false)}>
                取消
              </Button>
              <Button type="submit" disabled={pending}>
                {pending && <LoaderCircle className="size-4 animate-spin" aria-hidden="true" />}
                {pending ? "正在保存" : editing ? "更新密钥" : "添加密钥"}
              </Button>
            </div>
          </form>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
