import { useQuery } from "@tanstack/react-query";
import { Controller, useForm } from "react-hook-form";
import { Save } from "lucide-react";
import { useState } from "react";

import { queryKeys } from "@/api/query-keys";
import { getModels } from "@/api/system";
import { QueryError } from "@/components/common/query-error";
import { StatusMessage } from "@/components/common/status-message";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Switch } from "@/components/ui/switch";
import { usePreferencesStore, type UserPreferences } from "@/stores/preferences-store";

export function PreferencesForm() {
  const defaultModel = usePreferencesStore((state) => state.defaultModel);
  const ragEnabled = usePreferencesStore((state) => state.ragEnabled);
  const wikiEnabled = usePreferencesStore((state) => state.wikiEnabled);
  const setPreferences = usePreferencesStore((state) => state.setPreferences);
  const [saved, setSaved] = useState(false);
  const form = useForm<UserPreferences>({
    defaultValues: { defaultModel, ragEnabled, wikiEnabled },
  });
  const models = useQuery({
    queryKey: queryKeys.system.models,
    queryFn: ({ signal }) => getModels(signal),
    staleTime: 5 * 60_000,
  });

  const onSubmit = (values: UserPreferences) => {
    setPreferences(values);
    setSaved(true);
  };

  return (
    <section className="rounded-2xl border bg-surface shadow-xs">
      <div className="border-b px-5 py-4 sm:px-6">
        <h2 className="text-base font-semibold">对话默认值</h2>
        <p className="mt-1 text-xs leading-5 text-muted">
          这些偏好仅保存在当前设备，不会包含问题、文档或密钥。
        </p>
      </div>
      <form className="space-y-6 p-5 sm:p-6" onSubmit={form.handleSubmit(onSubmit)}>
        <div className="space-y-2">
          <Label htmlFor="default-model">默认模型</Label>
          {models.isPending ? (
            <Skeleton className="h-11 w-full" />
          ) : models.isError ? (
            <QueryError
              message="模型列表读取失败，当前编辑内容未被更改"
              onRetry={() => void models.refetch()}
            />
          ) : (
            <select
              id="default-model"
              className="h-11 w-full rounded-xl border bg-surface px-3.5 text-sm outline-none focus-visible:border-primary focus-visible:ring-3 focus-visible:ring-primary/15"
              {...form.register("defaultModel")}
            >
              <option value="">跟随后端默认模型</option>
              {models.data?.local_models.length ? (
                <optgroup label="本地模型">
                  {models.data.local_models.map((model) => (
                    <option key={model} value={model}>
                      {model}
                    </option>
                  ))}
                </optgroup>
              ) : null}
              {models.data?.online_models.length ? (
                <optgroup label="在线模型">
                  {models.data.online_models.map((model) => (
                    <option key={model} value={model}>
                      {model}
                    </option>
                  ))}
                </optgroup>
              ) : null}
            </select>
          )}
        </div>

        <Controller
          name="ragEnabled"
          control={form.control}
          render={({ field }) => (
            <div className="flex items-center justify-between gap-5 rounded-xl border p-4">
              <div>
                <Label htmlFor="default-rag">默认启用 RAG</Label>
                <p className="mt-1 text-xs leading-5 text-muted">新对话默认检索所选知识库。</p>
              </div>
              <Switch
                id="default-rag"
                checked={field.value}
                onCheckedChange={field.onChange}
                aria-label="默认启用 RAG"
              />
            </div>
          )}
        />

        <Controller
          name="wikiEnabled"
          control={form.control}
          render={({ field }) => (
            <div className="flex items-center justify-between gap-5 rounded-xl border p-4">
              <div>
                <Label htmlFor="default-wiki">默认启用 Wiki</Label>
                <p className="mt-1 text-xs leading-5 text-muted">新对话默认结合维基百科知识。</p>
              </div>
              <Switch
                id="default-wiki"
                checked={field.value}
                onCheckedChange={field.onChange}
                aria-label="默认启用 Wiki"
              />
            </div>
          )}
        />

        {saved && <StatusMessage tone="success">默认设置已保存到当前设备</StatusMessage>}
        <div className="flex justify-end">
          <Button type="submit" onClick={() => setSaved(false)}>
            <Save className="size-4" aria-hidden="true" />
            保存默认设置
          </Button>
        </div>
      </form>
    </section>
  );
}
