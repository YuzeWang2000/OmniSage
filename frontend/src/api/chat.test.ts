import type { AxiosResponse } from "axios";
import { describe, expect, it, vi } from "vitest";

import { streamChat } from "@/api/chat";
import { apiClient } from "@/api/client";
import type { ApiSchemas } from "@/api/types";

const payload: ApiSchemas["NormalizedChatRequest"] = {
  conversation_id: 1,
  messages: [{ role: "user", content: [{ type: "text", text: "hello" }], metadata: {} }],
  model_key: "ollama::test::model",
  workflow: "direct_chat",
  options: { reasoning: "auto", structured_output: false, tools: [] },
  retrieval: { enabled: false, wiki: false, use_reranker: true, top_k: 5, score_threshold: 0.5 },
  model_slots: {},
  regenerate: false,
};

describe("streamChat", () => {
  it("parses SSE events even when a frame is split across chunks", async () => {
    const encoder = new TextEncoder();
    const body = new ReadableStream<Uint8Array>({
      start(controller) {
        controller.enqueue(encoder.encode('data: {"type":"content_delta","content":"Hel'));
        controller.enqueue(encoder.encode('lo"}\r\n\r\ndata: {"type":"done"}\r\n\r\n'));
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

  it("keeps reasoning and answer streams separate", async () => {
    const encoder = new TextEncoder();
    const body = new ReadableStream<Uint8Array>({
      start(controller) {
        controller.enqueue(encoder.encode(
          'data: {"type":"reasoning_delta","content":"think"}\n\n' +
          'data: {"type":"content_delta","content":"answer"}\n\n' +
          'data: {"type":"usage","input_tokens":2,"output_tokens":3}\n\n' +
          'data: {"type":"done"}\n\n',
        ));
        controller.close();
      },
    });
    vi.spyOn(apiClient, "request").mockResolvedValue({ data: body } as AxiosResponse<ReadableStream<Uint8Array>>);
    const answer: string[] = [];
    const reasoning: string[] = [];
    await streamChat(payload, {
      onChunk: (chunk) => answer.push(chunk),
      onReasoning: (chunk) => reasoning.push(chunk),
    });
    expect(answer).toEqual(["answer"]);
    expect(reasoning).toEqual(["think"]);
  });

  it("rejects a stream that ends without done", async () => {
    const encoder = new TextEncoder();
    const body = new ReadableStream<Uint8Array>({
      start(controller) {
        controller.enqueue(encoder.encode('data: {"type":"content_delta","content":"partial"}\n\n'));
        controller.close();
      },
    });
    vi.spyOn(apiClient, "request").mockResolvedValue({ data: body } as AxiosResponse<ReadableStream<Uint8Array>>);
    await expect(streamChat(payload, { onChunk: vi.fn() })).rejects.toMatchObject({ kind: "unavailable" });
  });
});
