import type { Page, Route } from "@playwright/test";

const now = "2026-08-11T08:00:00Z";

export interface MockConversation {
  id: number;
  user_id: number;
  title: string;
  created_at: string;
  updated_at: string;
  is_active: boolean;
  message_count: number;
}

export interface MockKnowledgeBase {
  id: number;
  user_id: number;
  name: string;
  description: string | null;
  embedding_model: string;
  vector_db_path: string | null;
  file_count: number;
  document_count: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface MockApiState {
  conversations: MockConversation[];
  knowledgeBases: MockKnowledgeBase[];
  files: Array<{
    id: number;
    knowledge_base_id: number;
    filename: string;
    original_filename: string;
    file_path: string;
    file_size: number;
    file_type: string;
    document_count: number;
    is_processed: boolean;
    created_at: string;
    updated_at: string;
  }>;
  connections: Array<Record<string, unknown>>;
}

const json = (route: Route, body: unknown, status = 200) =>
  route.fulfill({
    status,
    contentType: "application/json",
    body: JSON.stringify(body),
  });

export async function installMockApi(page: Page) {
  const state: MockApiState = {
    conversations: [
      {
        id: 41,
        user_id: 7,
        title: "产品手册问答",
        created_at: now,
        updated_at: now,
        is_active: true,
        message_count: 2,
      },
    ],
    knowledgeBases: [
      {
        id: 91,
        user_id: 7,
        name: "产品文档",
        description: "已索引的产品说明资料",
        embedding_model: "nomic-embed-text",
        vector_db_path: null,
        file_count: 1,
        document_count: 12,
        is_active: true,
        created_at: now,
        updated_at: now,
      },
    ],
    files: [],
    connections: [],
  };

  await page.route("**/api/**", async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    if (!url.pathname.startsWith("/api/")) return route.fallback();
    const path = url.pathname.replace(/^\/api/, "") || "/";
    const method = request.method();

    if (path === "/health" && method === "GET") return json(route, { status: "ok" });
    if (path === "/ai/models" && method === "GET") {
      return json(route, [{key:"ollama::local::qwen-local",connection_id:"local",provider:"ollama",id:"qwen-local",display_name:"Qwen Local",source:"local_runtime",available:true,task_types:["chat"],input_modalities:["text"],output_modalities:["text"],capabilities:{streaming:true,reasoning:null,reasoning_toggle:null,reasoning_efforts:[],tools:false,structured_output:false,json_output:false,function_calling:false},limits:{},metadata:{},fetched_at:now,stale:false,vision:false}]);
    }
    if (path === "/auth/me" && method === "GET") {
      return json(route, { user_id: 7, username: "e2e-user" });
    }
    if (path === "/auth/login" && method === "POST") {
      return json(route, {
        user_id: 7,
        username: "e2e-user",
        access_token: crypto.randomUUID(),
        token_type: "bearer",
      });
    }

    if (path === "/conversations/user/7" && method === "GET") {
      return json(route, { conversations: state.conversations });
    }
    if (path === "/conversations/" && method === "POST") {
      const conversation: MockConversation = {
        id: 42,
        user_id: 7,
        title: "新对话",
        created_at: now,
        updated_at: now,
        is_active: true,
        message_count: 0,
      };
      state.conversations.unshift(conversation);
      return json(route, conversation);
    }
    const conversationMatch = path.match(/^\/conversations\/(\d+)$/);
    if (conversationMatch && method === "PATCH") {
      const id = Number(conversationMatch[1]);
      const body = request.postDataJSON() as { title: string };
      const conversation = state.conversations.find((item) => item.id === id);
      if (conversation) conversation.title = body.title;
      return json(route, { message: "updated", title: body.title });
    }
    if (conversationMatch && method === "DELETE") {
      const id = Number(conversationMatch[1]);
      state.conversations = state.conversations.filter((item) => item.id !== id);
      return json(route, { message: "deleted" });
    }
    const messagesMatch = path.match(/^\/conversations\/(\d+)\/messages$/);
    if (messagesMatch && method === "GET") {
      return json(route, {
        conversation_id: Number(messagesMatch[1]),
        messages: [
          { role: "user", content: [{type:"text",text:"如何使用产品搜索？"}] },
          { role: "assistant", content: [{type:"text",text:"可以在搜索页选择知识库并输入关键词。"}], model_key:"ollama::local::qwen-local" },
        ],
      });
    }

    if (path === "/chat/stream" && method === "POST") {
      return route.fulfill({
        status: 200,
        contentType: "text/event-stream",
        headers: { "cache-control": "no-cache", "x-accel-buffering": "no" },
        body:
          'data: {"type":"content_delta","content":"**测试回答**"}\n\n' +
          'data: {"type":"content_delta","content":"\\n\\n已根据可信来源完成回答。"}\n\n' +
          'data: {"type":"done"}\n\n',
      });
    }

    if (path === "/rag/stats/7" && method === "GET") {
      return json(route, {
        total_knowledge_bases: state.knowledgeBases.length,
        total_files: state.knowledgeBases.reduce((total, item) => total + item.file_count, 0),
        total_documents: state.knowledgeBases.reduce(
          (total, item) => total + item.document_count,
          0,
        ),
        active_knowledge_bases: state.knowledgeBases.length,
      });
    }
    if (path === "/rag/knowledge-bases/7" && method === "GET") {
      return json(route, { knowledge_bases: state.knowledgeBases });
    }
    if (path === "/rag/knowledge-bases" && method === "POST") {
      const body = request.postDataJSON() as {
        name: string;
        description: string | null;
        embedding_model: string;
      };
      const knowledgeBase: MockKnowledgeBase = {
        id: 92,
        user_id: 7,
        name: body.name,
        description: body.description,
        embedding_model: body.embedding_model,
        vector_db_path: null,
        file_count: 0,
        document_count: 0,
        is_active: true,
        created_at: now,
        updated_at: now,
      };
      state.knowledgeBases.unshift(knowledgeBase);
      return json(route, knowledgeBase);
    }

    const filesMatch = path.match(/^\/rag\/knowledge-bases\/(\d+)\/files$/);
    if (filesMatch && method === "GET") {
      const knowledgeBaseId = Number(filesMatch[1]);
      const files = state.files.filter((item) => item.knowledge_base_id === knowledgeBaseId);
      return json(route, { files, total: files.length });
    }
    if (filesMatch && method === "POST") {
      const knowledgeBaseId = Number(filesMatch[1]);
      state.files.push({
        id: 501,
        knowledge_base_id: knowledgeBaseId,
        filename: "indexed-guide.md",
        original_filename: "guide.md",
        file_path: "masked",
        file_size: 128,
        file_type: "md",
        document_count: 3,
        is_processed: true,
        created_at: now,
        updated_at: now,
      });
      const knowledgeBase = state.knowledgeBases.find((item) => item.id === knowledgeBaseId);
      if (knowledgeBase) {
        knowledgeBase.file_count = 1;
        knowledgeBase.document_count = 3;
      }
      return json(route, { message: "indexed", chunks: 3 });
    }

    const deleteFileMatch = path.match(/^\/rag\/knowledge-bases\/(\d+)\/files\/(\d+)$/);
    if (deleteFileMatch && method === "DELETE") {
      const fileId = Number(deleteFileMatch[2]);
      state.files = state.files.filter((item) => item.id !== fileId);
      return json(route, { message: "deleted" });
    }
    const deleteKnowledgeMatch = path.match(/^\/rag\/knowledge-bases\/(\d+)$/);
    if (deleteKnowledgeMatch && method === "DELETE") {
      const id = Number(deleteKnowledgeMatch[1]);
      state.knowledgeBases = state.knowledgeBases.filter((item) => item.id !== id);
      return json(route, { message: "deleted" });
    }

    const knowledgeSearchMatch = path.match(/^\/rag\/knowledge-bases\/(\d+)\/search$/);
    if (knowledgeSearchMatch && method === "GET") {
      const knowledgeBaseId = Number(knowledgeSearchMatch[1]);
      const knowledgeBase = state.knowledgeBases.find((item) => item.id === knowledgeBaseId);
      return json(route, {
        query: url.searchParams.get("query") || "",
        knowledge_base_id: knowledgeBaseId,
        knowledge_base_name: knowledgeBase?.name || "产品文档",
        threshold: 0.35,
        results: [
          {
            content: "完整的检索结果内容，用于验证结构化结果详情。",
            score: 0.93,
            source: "guide.md",
            page: 4,
            section: "搜索功能",
          },
        ],
      });
    }

    if (path === "/rag/wiki/status" && method === "GET") {
      return json(route, { success: true, mode: "online", stats: { total_articles: 120 } });
    }
    if (path === "/rag/wiki/switch-mode" && method === "POST") {
      return json(route, {
        success: true,
        message: "switched",
        mode: url.searchParams.get("mode") || "online",
        stats: { total_articles: 120 },
      });
    }
    if (path === "/rag/wiki/search" && method === "GET") {
      return json(route, {
        query: url.searchParams.get("query") || "",
        mode: "online",
        results: [
          {
            title: "检索增强生成",
            content: "RAG 将检索到的可信上下文提供给生成模型。",
            url: "https://example.com/rag",
            categories: ["人工智能"],
            score: 0.96,
            source: "Wikipedia",
          },
        ],
      });
    }

    if (path === "/ai/connections" && method === "GET") {
      return json(route, state.connections);
    }
    if (path === "/ai/connections" && method === "POST") {
      const body = request.postDataJSON() as { provider: string; display_name: string };
      const connection = {
        id: "connection-801",
        provider: body.provider,
        display_name: body.display_name,
        protocol: body.provider === "ollama" ? "ollama" : "openai_compatible",
        base_url: "https://api.example.invalid",
        config: {},
        is_active: true,
        has_credential: true,
        masked_credential: "sk-••••ret",
        credential_version: 1,
      };
      state.connections.push(connection);
      return json(route, connection, 201);
    }
    const connectionAction = path.match(/^\/ai\/connections\/([^/]+)\/(test|models\/refresh)$/);
    if (connectionAction && method === "POST") {
      if (connectionAction[2] === "test") return json(route, { ok: true, message: "连接成功" });
      return json(route, []);
    }

    return json(route, { detail: `Unhandled mock endpoint: ${method} ${path}` }, 501);
  });

  return state;
}

export async function seedAuthenticatedSession(page: Page) {
  await page.addInitScript(() => {
    sessionStorage.setItem(
      "omnisage-auth",
      JSON.stringify({
        state: {
          token: crypto.randomUUID(),
          user: { user_id: 7, username: "e2e-user" },
        },
        version: 0,
      }),
    );
  });
}
