import * as Dialog from "@radix-ui/react-dialog";
import { ExternalLink, X } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { SearchDisplayResult } from "@/features/search/types";

function safeHttpUrl(value?: string | null) {
  if (!value) return null;
  try {
    const url = new URL(value);
    return url.protocol === "http:" || url.protocol === "https:" ? url.toString() : null;
  } catch {
    return null;
  }
}

interface SearchResultDialogProps {
  result: SearchDisplayResult | null;
  onOpenChange: (open: boolean) => void;
}

export function SearchResultDialog({ result, onOpenChange }: SearchResultDialogProps) {
  const href = safeHttpUrl(result?.url);
  return (
    <Dialog.Root open={Boolean(result)} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-50 bg-[#101828]/45 backdrop-blur-[2px]" />
        <Dialog.Content className="fixed left-1/2 top-1/2 z-50 max-h-[calc(100vh-24px)] w-[calc(100vw-24px)] max-w-3xl -translate-x-1/2 -translate-y-1/2 overflow-y-auto rounded-2xl border bg-surface p-5 shadow-2xl outline-none sm:p-7">
          <div className="flex min-w-0 items-start justify-between gap-4">
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <Badge>{result?.kind === "wiki" ? "Wiki" : "知识库"}</Badge>
                {result?.score != null && (
                  <Badge tone="success">
                    相关度 {(Math.max(0, Math.min(1, result.score)) * 100).toFixed(1)}%
                  </Badge>
                )}
              </div>
              <Dialog.Title className="mt-3 break-words text-xl font-semibold">
                {result?.title}
              </Dialog.Title>
              <Dialog.Description className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted">
                <span>来源：{result?.source}</span>
                {result?.page != null && <span>第 {result.page} 页</span>}
                {result?.section && <span>章节：{result.section}</span>}
              </Dialog.Description>
            </div>
            <Dialog.Close asChild>
              <Button variant="ghost" size="icon" aria-label="关闭搜索结果详情">
                <X className="size-4" />
              </Button>
            </Dialog.Close>
          </div>

          <div className="mt-6 whitespace-pre-wrap break-words rounded-xl border bg-[#fafbfb] p-4 text-sm leading-7 sm:p-5">
            {result?.content}
          </div>
          {result?.categories?.length ? (
            <div className="mt-5 flex flex-wrap gap-2" aria-label="Wiki 分类">
              {result.categories.map((category) => (
                <Badge key={category}>{category}</Badge>
              ))}
            </div>
          ) : null}
          {href && (
            <div className="mt-6 flex justify-end">
              <Button asChild variant="secondary">
                <a href={href} target="_blank" rel="noopener noreferrer nofollow">
                  查看原始来源
                  <ExternalLink className="size-4" aria-hidden="true" />
                </a>
              </Button>
            </div>
          )}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
