import { FileUp, LoaderCircle, UploadCloud, X } from "lucide-react";
import { useRef, useState } from "react";

import { uploadKnowledgeFile } from "@/api/knowledge";
import type { ApiSchemas } from "@/api/types";
import { Button } from "@/components/ui/button";
import { validateKnowledgeFile } from "@/features/knowledge/file-validation";
import { cn } from "@/utils/cn";

interface FileUploaderProps {
  knowledgeBaseId: number;
  onUploaded: (response: ApiSchemas["FileUploadResponse"]) => void;
}

export function FileUploader({ knowledgeBaseId, onUploaded }: FileUploaderProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const controllerRef = useRef<AbortController | null>(null);
  const [dragging, setDragging] = useState(false);
  const [progress, setProgress] = useState(0);
  const [pending, setPending] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const upload = async (file: File) => {
    const validationError = validateKnowledgeFile(file);
    if (validationError) {
      setError(validationError);
      setSuccess(null);
      return;
    }

    const controller = new AbortController();
    controllerRef.current = controller;
    setPending(true);
    setProgress(0);
    setFileName(file.name);
    setError(null);
    setSuccess(null);
    try {
      const response = await uploadKnowledgeFile(knowledgeBaseId, file, {
        signal: controller.signal,
        onProgress: setProgress,
      });
      setSuccess(`${file.name} 已完成索引，共 ${response.chunks ?? 0} 个文档块。`);
      onUploaded(response);
    } catch (uploadError) {
      const cancelled = controller.signal.aborted;
      setError(
        cancelled
          ? "上传已取消。"
          : uploadError instanceof Error
            ? uploadError.message
            : "上传或索引失败，请重试。",
      );
    } finally {
      setPending(false);
      controllerRef.current = null;
      if (inputRef.current) inputRef.current.value = "";
    }
  };

  return (
    <section
      className="rounded-2xl border bg-surface p-4 shadow-xs sm:p-5"
      aria-labelledby="upload-title"
    >
      <div className="flex items-center justify-between gap-3">
        <div>
          <h3 id="upload-title" className="text-sm font-semibold">
            上传文档
          </h3>
          <p className="mt-1 text-xs text-muted">支持 PDF、TXT、MD、DOC、DOCX，单文件最大 10MB。</p>
        </div>
        <FileUp className="size-5 text-primary" aria-hidden="true" />
      </div>
      <input
        ref={inputRef}
        className="sr-only"
        id="knowledge-file"
        type="file"
        accept=".pdf,.txt,.md,.doc,.docx"
        disabled={pending}
        onChange={(event) => {
          const file = event.target.files?.[0];
          if (file) void upload(file);
        }}
      />
      <label
        htmlFor="knowledge-file"
        className={cn(
          "mt-4 flex min-h-32 cursor-pointer flex-col items-center justify-center rounded-xl border border-dashed px-4 py-5 text-center transition-colors",
          dragging ? "border-primary bg-[#eef7f3]" : "bg-[#fafbfb] hover:bg-[#f5f8f7]",
          pending && "pointer-events-none opacity-70",
        )}
        onDragEnter={(event) => {
          event.preventDefault();
          setDragging(true);
        }}
        onDragOver={(event) => event.preventDefault()}
        onDragLeave={(event) => {
          event.preventDefault();
          setDragging(false);
        }}
        onDrop={(event) => {
          event.preventDefault();
          setDragging(false);
          if (pending) return;
          const file = event.dataTransfer.files[0];
          if (file) void upload(file);
        }}
      >
        <span className="grid size-10 place-items-center rounded-xl bg-[#eaf4f0] text-primary">
          <UploadCloud className="size-5" aria-hidden="true" />
        </span>
        <span className="mt-3 text-sm font-medium">点击选择或拖放文件</span>
        <span className="mt-1 text-xs text-muted">文件将直接发送到已配置的 FastAPI 后端</span>
      </label>

      {pending && (
        <div className="mt-4 rounded-xl border bg-[#f8faf9] p-3" aria-live="polite">
          <div className="flex items-center gap-3">
            <LoaderCircle
              className="size-4 shrink-0 animate-spin text-primary"
              aria-hidden="true"
            />
            <div className="min-w-0 flex-1">
              <p className="truncate text-xs font-medium">{fileName}</p>
              <p className="mt-1 text-[11px] text-muted">
                {progress >= 100 ? "上传完成，正在解析并建立索引…" : `正在上传 ${progress}%`}
              </p>
            </div>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="size-9 min-h-9"
              onClick={() => controllerRef.current?.abort()}
              aria-label="取消上传"
            >
              <X className="size-4" aria-hidden="true" />
            </Button>
          </div>
          <div
            className="mt-3 h-1.5 overflow-hidden rounded-full bg-[#e4e7ec]"
            role="progressbar"
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={progress}
          >
            <div
              className="h-full rounded-full bg-primary transition-[width]"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}
      {error && (
        <p
          className="mt-3 rounded-xl border border-[#fecdca] bg-[#fef3f2] px-3 py-2 text-xs text-danger"
          role="alert"
        >
          {error}
        </p>
      )}
      {success && (
        <p
          className="mt-3 rounded-xl border border-[#abefc6] bg-[#ecfdf3] px-3 py-2 text-xs text-[#067647]"
          role="status"
        >
          {success}
        </p>
      )}
    </section>
  );
}
