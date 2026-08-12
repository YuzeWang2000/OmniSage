import type { AxiosResponse } from "axios";
import { describe, expect, it, vi } from "vitest";

import { streamChat } from "@/api/chat";
import { apiClient } from "@/api/client";
import type { ApiSchemas } from "@/api/types";

const payload: ApiSchemas["ChatRequest"] = {
  conversation_id: 1,
  message: "hello",
  model: "test-model",
  mode: "chat",
  use_rag: false,
  use_wiki: false,
  stream: true,
  regenerate: false,
  chain_type: "stuff",
  prompt_name: "chat_default",
  use_reranker: true,
  top_k: 5,
  score_threshold: 0.5,
};

describe("streamChat", () => {
  it("parses SSE events even when a frame is split across chunks", async () => {
    const encoder = new TextEncoder();
    const body = new ReadableStream<Uint8Array>({
      start(controller) {
        controller.enqueue(encoder.encode('data: {"chunk":"Hel'));
        controller.enqueue(encoder.encode('lo"}\r\n\r\ndata: {"done":true}\r\n\r\n'));
        controller.close();
      },
    });
    vi.spyOn(apiClient, "request").mockResolvedValue({ data: body } as AxiosResponse<
      ReadableStream<Uint8Array>
    >);
    const chunks: string[] = [];

    await streamChat(payload, { onChunk: (chunk) => chunks.push(chunk) });

    expect(chunks).toEqual(["Hello"]);
  });
});
