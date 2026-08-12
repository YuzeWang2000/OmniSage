import type { AxiosResponse } from "axios";

import { ApiError, apiClient } from "@/api/client";
import type { ApiSchemas } from "@/api/types";

export interface ChatStreamEvent {
  chunk?: string;
  done?: boolean;
  error?: string;
}

interface StreamChatOptions {
  signal?: AbortSignal;
  onChunk: (chunk: string) => void;
}

const parseTimeout = () => {
  const configured = Number(import.meta.env.VITE_CHAT_TIMEOUT_MS);
  return Number.isFinite(configured) && configured > 0 ? configured : 180_000;
};

function parseEvent(frame: string): ChatStreamEvent | null {
  const payload = frame
    .split("\n")
    .filter((line) => line.startsWith("data:"))
    .map((line) => line.slice(5).trimStart())
    .join("\n");
  if (!payload) return null;

  try {
    return JSON.parse(payload) as ChatStreamEvent;
  } catch {
    throw new ApiError("回答流格式无效，请重试", { kind: "server" });
  }
}

export async function streamChat(
  payload: ApiSchemas["ChatRequest"],
  { signal, onChunk }: StreamChatOptions,
) {
  const response = await apiClient.request<
    ReadableStream<Uint8Array>,
    AxiosResponse<ReadableStream<Uint8Array>>,
    ApiSchemas["ChatRequest"]
  >({
    method: "POST",
    url: "/chat/stream",
    data: payload,
    responseType: "stream",
    timeout: parseTimeout(),
    signal,
    headers: { Accept: "text/event-stream" },
  });

  if (!response.data || typeof response.data.getReader !== "function") {
    throw new ApiError("浏览器未收到可读取的回答流", { kind: "server" });
  }

  const reader = response.data.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let completed = false;

  const handleEvent = (event: ChatStreamEvent | null) => {
    if (!event) return;
    if (event.error) throw new ApiError(event.error, { kind: "server" });
    if (event.chunk) onChunk(event.chunk);
    if (event.done) completed = true;
  };

  try {
    while (true) {
      const { done, value } = await reader.read();
      buffer = `${buffer}${decoder.decode(value, { stream: !done })}`.replace(/\r\n/g, "\n");

      let boundary = buffer.indexOf("\n\n");
      while (boundary >= 0) {
        const frame = buffer.slice(0, boundary);
        buffer = buffer.slice(boundary + 2);
        handleEvent(parseEvent(frame));
        boundary = buffer.indexOf("\n\n");
      }

      if (done) break;
    }
    if (buffer.trim()) handleEvent(parseEvent(buffer));
  } catch (error) {
    if (signal?.aborted) {
      throw new ApiError("请求已取消", { kind: "cancelled", cause: error });
    }
    throw error;
  } finally {
    reader.releaseLock();
  }

  if (!completed) {
    throw new ApiError("回答流意外中断，请重试", { kind: "unavailable" });
  }
}
