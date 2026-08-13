export interface paths {
    "/auth/register": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Register
         * @description 用户注册接口
         */
        post: operations["register_auth_register_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/auth/login": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Login
         * @description 用户登录接口
         */
        post: operations["login_auth_login_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/auth/me": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Get Me
         * @description 返回 Bearer Token 对应的当前用户，用于客户端恢复登录状态。
         */
        get: operations["get_me_auth_me_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/chat/stream": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Chat Stream Endpoint */
        post: operations["chat_stream_endpoint_chat_stream_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/rag/knowledge-bases": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Create Knowledge Base
         * @description 创建知识库
         */
        post: operations["create_knowledge_base_rag_knowledge_bases_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/rag/knowledge-bases/{user_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Get User Knowledge Bases
         * @description 获取用户的知识库列表
         */
        get: operations["get_user_knowledge_bases_rag_knowledge_bases__user_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/rag/knowledge-bases/{knowledge_base_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post?: never;
        /**
         * Delete Knowledge Base
         * @description 删除知识库
         */
        delete: operations["delete_knowledge_base_rag_knowledge_bases__knowledge_base_id__delete"];
        options?: never;
        head?: never;
        /** Update Knowledge Base */
        patch: operations["update_knowledge_base_rag_knowledge_bases__knowledge_base_id__patch"];
        trace?: never;
    };
    "/rag/knowledge-bases/{knowledge_base_id}/files": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Get Knowledge Base Files
         * @description 获取知识库的文件列表
         */
        get: operations["get_knowledge_base_files_rag_knowledge_bases__knowledge_base_id__files_get"];
        put?: never;
        /**
         * Upload File To Knowledge Base
         * @description 上传文件到指定知识库
         */
        post: operations["upload_file_to_knowledge_base_rag_knowledge_bases__knowledge_base_id__files_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/rag/knowledge-bases/{knowledge_base_id}/search": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Search Knowledge Base
         * @description 使用已有向量检索能力搜索用户指定的知识库。
         */
        get: operations["search_knowledge_base_rag_knowledge_bases__knowledge_base_id__search_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/rag/knowledge-bases/{knowledge_base_id}/files/{file_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post?: never;
        /**
         * Delete File From Knowledge Base
         * @description 从知识库中删除文件
         */
        delete: operations["delete_file_from_knowledge_base_rag_knowledge_bases__knowledge_base_id__files__file_id__delete"];
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/rag/stats/{user_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Get User Knowledge Base Stats
         * @description 获取用户的知识库统计信息
         */
        get: operations["get_user_knowledge_base_stats_rag_stats__user_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/rag/enhance-context-with-wiki": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Enhance Context With Wiki
         * @description 使用Wiki知识增强上下文
         */
        get: operations["enhance_context_with_wiki_rag_enhance_context_with_wiki_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/rag/wiki/search": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Search Wiki
         * @description 使用当前 Wiki 模式返回可用于引用展示的结构化结果。
         */
        get: operations["search_wiki_rag_wiki_search_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/rag/wiki/status": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Get Wiki Status
         * @description 获取Wiki数据状态
         */
        get: operations["get_wiki_status_rag_wiki_status_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/rag/wiki/switch-mode": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Switch Wiki Mode
         * @description 切换Wiki服务模式
         */
        post: operations["switch_wiki_mode_rag_wiki_switch_mode_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/conversations/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Create Conversation
         * @description 创建新对话
         */
        post: operations["create_conversation_conversations__post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/conversations/user/{user_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Get User Conversations
         * @description 获取用户的所有对话
         */
        get: operations["get_user_conversations_conversations_user__user_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/conversations/{conversation_id}/messages": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Get Conversation Messages
         * @description 获取指定对话的聊天历史
         */
        get: operations["get_conversation_messages_conversations__conversation_id__messages_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/conversations/{conversation_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post?: never;
        /**
         * Delete Conversation
         * @description 删除对话
         */
        delete: operations["delete_conversation_conversations__conversation_id__delete"];
        options?: never;
        head?: never;
        /**
         * Rename Conversation
         * @description 重命名属于当前用户的对话。
         */
        patch: operations["rename_conversation_conversations__conversation_id__patch"];
        trace?: never;
    };
    "/ai/providers": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Providers */
        get: operations["providers_ai_providers_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/ai/connections": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Connections */
        get: operations["connections_ai_connections_get"];
        put?: never;
        /** Create Connection */
        post: operations["create_connection_ai_connections_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/ai/connections/{connection_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Connection */
        get: operations["get_connection_ai_connections__connection_id__get"];
        /** Update Connection */
        put: operations["update_connection_ai_connections__connection_id__put"];
        post?: never;
        /** Delete Connection */
        delete: operations["delete_connection_ai_connections__connection_id__delete"];
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/ai/connections/{connection_id}/test": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Test Connection */
        post: operations["test_connection_ai_connections__connection_id__test_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/ai/connections/{connection_id}/models": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Connection Models */
        get: operations["connection_models_ai_connections__connection_id__models_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/ai/connections/{connection_id}/models/refresh": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Refresh Models */
        post: operations["refresh_models_ai_connections__connection_id__models_refresh_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/ai/models": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Models */
        get: operations["models_ai_models_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/ai/models/{model_key}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Model */
        get: operations["model_ai_models__model_key__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/health": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Health Check */
        get: operations["health_check_health_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
}
export type webhooks = Record<string, never>;
export interface components {
    schemas: {
        /** AudioPart */
        AudioPart: {
            /**
             * @description discriminator enum property added by openapi-typescript
             * @enum {string}
             */
            type: "audio";
            /** Asset Id */
            asset_id: string;
        };
        /** AuthResponse */
        AuthResponse: {
            /** User Id */
            user_id: number;
            /** Username */
            username: string;
            /** Access Token */
            access_token: string;
            /**
             * Token Type
             * @default bearer
             */
            token_type: string;
        };
        /** Body_upload_file_to_knowledge_base_rag_knowledge_bases__knowledge_base_id__files_post */
        Body_upload_file_to_knowledge_base_rag_knowledge_bases__knowledge_base_id__files_post: {
            /**
             * File
             * Format: binary
             */
            file: string;
        };
        /** ChatMessageResponse */
        ChatMessageResponse: {
            /** Role */
            role: string;
            /** Content */
            content: {
                [key: string]: unknown;
            }[];
            /** Model Key */
            model_key?: string | null;
        };
        /** ChatOptions */
        ChatOptions: {
            /** @default auto */
            reasoning: components["schemas"]["ReasoningMode"];
            /** Reasoning Effort */
            reasoning_effort?: string | null;
            /** Temperature */
            temperature?: number | null;
            /**
             * Structured Output
             * @default false
             */
            structured_output: boolean;
            /** Tools */
            tools?: {
                [key: string]: unknown;
            }[];
        };
        /** ConnectionCreate */
        ConnectionCreate: {
            provider: components["schemas"]["ProviderType"];
            /** Display Name */
            display_name: string;
            /** Region */
            region?: string | null;
            /** Base Url */
            base_url?: string | null;
            /** Workspace Id */
            workspace_id?: string | null;
            /** Api Key */
            api_key?: string | null;
            /** Manual Models */
            manual_models?: string[];
            /** Manual Model Capabilities */
            manual_model_capabilities?: {
                [key: string]: components["schemas"]["ModelCapabilities"];
            };
            /**
             * Is Active
             * @default true
             */
            is_active: boolean;
        };
        /** ConnectionUpdate */
        ConnectionUpdate: {
            /** Display Name */
            display_name?: string | null;
            /** Region */
            region?: string | null;
            /** Base Url */
            base_url?: string | null;
            /** Workspace Id */
            workspace_id?: string | null;
            /** Api Key */
            api_key?: string | null;
            /** Manual Models */
            manual_models?: string[] | null;
            /** Manual Model Capabilities */
            manual_model_capabilities?: {
                [key: string]: components["schemas"]["ModelCapabilities"];
            } | null;
            /** Is Active */
            is_active?: boolean | null;
        };
        /** ConversationCreate */
        ConversationCreate: {
            /** User Id */
            user_id?: number | null;
            /** Title */
            title: string;
        };
        /** ConversationListResponse */
        ConversationListResponse: {
            /** Conversations */
            conversations: components["schemas"]["ConversationResponse"][];
        };
        /** ConversationMessagesResponse */
        ConversationMessagesResponse: {
            /** Conversation Id */
            conversation_id: number;
            /** Messages */
            messages: components["schemas"]["ChatMessageResponse"][];
        };
        /** ConversationResponse */
        ConversationResponse: {
            /** Id */
            id: number;
            /** User Id */
            user_id: number;
            /** Title */
            title: string;
            /**
             * Created At
             * Format: date-time
             */
            created_at: string;
            /**
             * Updated At
             * Format: date-time
             */
            updated_at: string;
            /** Is Active */
            is_active: boolean;
            /**
             * Message Count
             * @default 0
             */
            message_count: number;
        };
        /** ConversationUpdate */
        ConversationUpdate: {
            /** User Id */
            user_id?: number | null;
            /** Title */
            title: string;
        };
        /** DocumentPart */
        DocumentPart: {
            /**
             * @description discriminator enum property added by openapi-typescript
             * @enum {string}
             */
            type: "document";
            /** Asset Id */
            asset_id: string;
        };
        /** FileUploadResponse */
        FileUploadResponse: {
            /** Message */
            message: string;
            /**
             * Chunks
             * @default 0
             */
            chunks: number | null;
        };
        /** HTTPValidationError */
        HTTPValidationError: {
            /** Detail */
            detail?: components["schemas"]["ValidationError"][];
        };
        /** ImagePart */
        ImagePart: {
            /**
             * @description discriminator enum property added by openapi-typescript
             * @enum {string}
             */
            type: "image";
            /** Asset Id */
            asset_id: string;
            /**
             * Detail
             * @default auto
             * @enum {string}
             */
            detail: "auto" | "low" | "high";
        };
        /** KnowledgeBaseCreate */
        KnowledgeBaseCreate: {
            /** User Id */
            user_id?: number | null;
            /** Name */
            name: string;
            /** Description */
            description?: string | null;
            /**
             * Embedding Model
             * @default nomic-embed-text
             */
            embedding_model: string;
        };
        /** KnowledgeBaseListResponse */
        KnowledgeBaseListResponse: {
            /** Knowledge Bases */
            knowledge_bases: components["schemas"]["KnowledgeBaseResponse"][];
        };
        /** KnowledgeBaseResponse */
        KnowledgeBaseResponse: {
            /** Id */
            id: number;
            /** User Id */
            user_id: number;
            /** Name */
            name: string;
            /** Description */
            description: string | null;
            /** Embedding Model */
            embedding_model: string;
            /** Vector Db Path */
            vector_db_path: string | null;
            /** File Count */
            file_count: number;
            /** Document Count */
            document_count: number;
            /** Is Active */
            is_active: boolean;
            /**
             * Created At
             * Format: date-time
             */
            created_at: string;
            /**
             * Updated At
             * Format: date-time
             */
            updated_at: string;
        };
        /** KnowledgeBaseSearchResponse */
        KnowledgeBaseSearchResponse: {
            /** Query */
            query: string;
            /** Knowledge Base Id */
            knowledge_base_id: number;
            /** Knowledge Base Name */
            knowledge_base_name: string;
            /** Threshold */
            threshold?: number | null;
            /** Results */
            results: components["schemas"]["KnowledgeBaseSearchResult"][];
        };
        /** KnowledgeBaseSearchResult */
        KnowledgeBaseSearchResult: {
            /** Content */
            content: string;
            /** Score */
            score: number;
            /** Source */
            source?: string | null;
            /** Page */
            page?: number | null;
            /** Section */
            section?: string | null;
        };
        /** KnowledgeBaseStats */
        KnowledgeBaseStats: {
            /** Total Knowledge Bases */
            total_knowledge_bases: number;
            /** Total Files */
            total_files: number;
            /** Total Documents */
            total_documents: number;
            /** Active Knowledge Bases */
            active_knowledge_bases: number;
        };
        /** KnowledgeBaseUpdate */
        KnowledgeBaseUpdate: {
            /** Name */
            name: string;
            /** Description */
            description?: string | null;
        };
        /** KnowledgeFileListResponse */
        KnowledgeFileListResponse: {
            /** Files */
            files: components["schemas"]["KnowledgeFileResponse"][];
            /** Total */
            total: number;
        };
        /** KnowledgeFileResponse */
        KnowledgeFileResponse: {
            /** Id */
            id: number;
            /** Knowledge Base Id */
            knowledge_base_id: number;
            /** Filename */
            filename: string;
            /** Original Filename */
            original_filename: string;
            /** File Path */
            file_path: string;
            /** File Size */
            file_size: number;
            /** File Type */
            file_type: string | null;
            /** Document Count */
            document_count: number;
            /** Is Processed */
            is_processed: boolean;
            /**
             * Created At
             * Format: date-time
             */
            created_at: string;
            /**
             * Updated At
             * Format: date-time
             */
            updated_at: string;
        };
        /**
         * Modality
         * @enum {string}
         */
        Modality: "text" | "image" | "audio" | "video" | "document";
        /** ModelCapabilities */
        ModelCapabilities: {
            /** Streaming */
            streaming?: boolean | null;
            /** Reasoning */
            reasoning?: boolean | null;
            /** Reasoning Toggle */
            reasoning_toggle?: boolean | null;
            /** Reasoning Efforts */
            reasoning_efforts?: string[];
            /** Tools */
            tools?: boolean | null;
            /** Structured Output */
            structured_output?: boolean | null;
            /** Json Output */
            json_output?: boolean | null;
            /** Function Calling */
            function_calling?: boolean | null;
        };
        /** ModelSlots */
        ModelSlots: {
            /** Generation Model Key */
            generation_model_key?: string | null;
            /** Embedding Model Key */
            embedding_model_key?: string | null;
            /** Rerank Model Key */
            rerank_model_key?: string | null;
            /** Speech Model Key */
            speech_model_key?: string | null;
        };
        /**
         * ModelTaskType
         * @enum {string}
         */
        ModelTaskType: "chat" | "text_generation" | "embedding" | "rerank" | "text_to_speech" | "speech_to_text" | "image_understanding" | "image_generation" | "video_understanding" | "video_generation";
        /** NormalizedChatRequest */
        NormalizedChatRequest: {
            /** Conversation Id */
            conversation_id: number;
            /** Messages */
            messages: components["schemas"]["NormalizedMessage"][];
            /** Model Key */
            model_key: string;
            /** @default direct_chat */
            workflow: components["schemas"]["WorkflowType"];
            options?: components["schemas"]["ChatOptions"];
            retrieval?: components["schemas"]["RetrievalOptions"];
            model_slots?: components["schemas"]["ModelSlots"];
            /**
             * Regenerate
             * @default false
             */
            regenerate: boolean;
        };
        /** NormalizedMessage */
        NormalizedMessage: {
            /**
             * Role
             * @enum {string}
             */
            role: "system" | "user" | "assistant" | "tool";
            /** Content */
            content: (components["schemas"]["TextPart"] | components["schemas"]["ImagePart"] | components["schemas"]["AudioPart"] | components["schemas"]["VideoPart"] | components["schemas"]["DocumentPart"] | components["schemas"]["ToolResultPart"])[];
            /** Name */
            name?: string | null;
            /** Tool Call Id */
            tool_call_id?: string | null;
            /** Metadata */
            metadata?: {
                [key: string]: unknown;
            };
        };
        /**
         * ProviderType
         * @enum {string}
         */
        ProviderType: "ollama" | "deepseek" | "dashscope";
        /**
         * ReasoningMode
         * @enum {string}
         */
        ReasoningMode: "off" | "auto" | "on";
        /** RetrievalOptions */
        RetrievalOptions: {
            /**
             * Enabled
             * @default false
             */
            enabled: boolean;
            /**
             * Wiki
             * @default false
             */
            wiki: boolean;
            /** Knowledge Base Id */
            knowledge_base_id?: number | null;
            /**
             * Use Reranker
             * @default true
             */
            use_reranker: boolean;
            /**
             * Top K
             * @default 5
             */
            top_k: number;
            /**
             * Score Threshold
             * @default 0.5
             */
            score_threshold: number;
        };
        /** TextPart */
        TextPart: {
            /**
             * @description discriminator enum property added by openapi-typescript
             * @enum {string}
             */
            type: "text";
            /** Text */
            text: string;
        };
        /** ToolResultPart */
        ToolResultPart: {
            /**
             * @description discriminator enum property added by openapi-typescript
             * @enum {string}
             */
            type: "tool_result";
            /** Tool Call Id */
            tool_call_id: string;
            /** Content */
            content: string;
        };
        /** UserCreate */
        UserCreate: {
            /** Username */
            username: string;
            /** Password */
            password: string;
        };
        /** UserLogin */
        UserLogin: {
            /** Username */
            username: string;
            /** Password */
            password: string;
        };
        /** UserResponse */
        UserResponse: {
            /** User Id */
            user_id: number;
            /** Username */
            username: string;
        };
        /** ValidationError */
        ValidationError: {
            /** Location */
            loc: (string | number)[];
            /** Message */
            msg: string;
            /** Error Type */
            type: string;
        };
        /** VideoPart */
        VideoPart: {
            /**
             * @description discriminator enum property added by openapi-typescript
             * @enum {string}
             */
            type: "video";
            /** Asset Id */
            asset_id: string;
        };
        /** WikiSearchResponse */
        WikiSearchResponse: {
            /** Query */
            query: string;
            /** Mode */
            mode: string;
            /** Results */
            results: components["schemas"]["WikiSearchResult"][];
        };
        /** WikiSearchResult */
        WikiSearchResult: {
            /** Title */
            title: string;
            /** Content */
            content: string;
            /** Url */
            url?: string | null;
            /** Categories */
            categories?: string[];
            /**
             * Score
             * @default 0
             */
            score: number;
            /** Source */
            source: string;
        };
        /**
         * WorkflowType
         * @enum {string}
         */
        WorkflowType: "direct_chat" | "grounded_chat" | "agent";
    };
    responses: never;
    parameters: never;
    requestBodies: never;
    headers: never;
    pathItems: never;
}
export type $defs = Record<string, never>;
export interface operations {
    register_auth_register_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["UserCreate"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["UserResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    login_auth_login_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["UserLogin"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AuthResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_me_auth_me_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["UserResponse"];
                };
            };
        };
    };
    chat_stream_endpoint_chat_stream_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["NormalizedChatRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    create_knowledge_base_rag_knowledge_bases_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["KnowledgeBaseCreate"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["KnowledgeBaseResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_user_knowledge_bases_rag_knowledge_bases__user_id__get: {
        parameters: {
            query?: {
                limit?: number | null;
            };
            header?: never;
            path: {
                user_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["KnowledgeBaseListResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    delete_knowledge_base_rag_knowledge_bases__knowledge_base_id__delete: {
        parameters: {
            query?: {
                /** @description 兼容字段：用户ID */
                user_id?: number | null;
            };
            header?: never;
            path: {
                knowledge_base_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    update_knowledge_base_rag_knowledge_bases__knowledge_base_id__patch: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                knowledge_base_id: number;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["KnowledgeBaseUpdate"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["KnowledgeBaseResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_knowledge_base_files_rag_knowledge_bases__knowledge_base_id__files_get: {
        parameters: {
            query?: {
                /** @description 兼容字段：用户ID */
                user_id?: number | null;
            };
            header?: never;
            path: {
                knowledge_base_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["KnowledgeFileListResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    upload_file_to_knowledge_base_rag_knowledge_bases__knowledge_base_id__files_post: {
        parameters: {
            query?: {
                /** @description 兼容字段：用户ID */
                user_id?: number | null;
            };
            header?: never;
            path: {
                knowledge_base_id: number;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "multipart/form-data": components["schemas"]["Body_upload_file_to_knowledge_base_rag_knowledge_bases__knowledge_base_id__files_post"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["FileUploadResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    search_knowledge_base_rag_knowledge_bases__knowledge_base_id__search_get: {
        parameters: {
            query: {
                /** @description 兼容字段：用户ID */
                user_id?: number | null;
                /** @description 查询内容 */
                query: string;
                /** @description 返回结果数量 */
                top_k?: number;
                /** @description 最低相关度 */
                min_score?: number | null;
            };
            header?: never;
            path: {
                knowledge_base_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["KnowledgeBaseSearchResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    delete_file_from_knowledge_base_rag_knowledge_bases__knowledge_base_id__files__file_id__delete: {
        parameters: {
            query?: {
                /** @description 兼容字段：用户ID */
                user_id?: number | null;
            };
            header?: never;
            path: {
                knowledge_base_id: number;
                file_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_user_knowledge_base_stats_rag_stats__user_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                user_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["KnowledgeBaseStats"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    enhance_context_with_wiki_rag_enhance_context_with_wiki_get: {
        parameters: {
            query: {
                /** @description 查询内容 */
                query: string;
                /** @description 现有上下文 */
                existing_context?: string;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    search_wiki_rag_wiki_search_get: {
        parameters: {
            query: {
                /** @description 查询内容 */
                query: string;
                /** @description 返回结果数量 */
                limit?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["WikiSearchResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_wiki_status_rag_wiki_status_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    switch_wiki_mode_rag_wiki_switch_mode_post: {
        parameters: {
            query: {
                /** @description 目标模式: online 或 offline */
                mode: string;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    create_conversation_conversations__post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ConversationCreate"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ConversationResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_user_conversations_conversations_user__user_id__get: {
        parameters: {
            query?: {
                limit?: number | null;
            };
            header?: never;
            path: {
                user_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ConversationListResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_conversation_messages_conversations__conversation_id__messages_get: {
        parameters: {
            query?: {
                user_id?: number | null;
            };
            header?: never;
            path: {
                conversation_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ConversationMessagesResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    delete_conversation_conversations__conversation_id__delete: {
        parameters: {
            query?: {
                user_id?: number | null;
            };
            header?: never;
            path: {
                conversation_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    rename_conversation_conversations__conversation_id__patch: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                conversation_id: number;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ConversationUpdate"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    providers_ai_providers_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    connections_ai_connections_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    create_connection_ai_connections_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ConnectionCreate"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_connection_ai_connections__connection_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                connection_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    update_connection_ai_connections__connection_id__put: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                connection_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ConnectionUpdate"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    delete_connection_ai_connections__connection_id__delete: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                connection_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            204: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    test_connection_ai_connections__connection_id__test_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                connection_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    connection_models_ai_connections__connection_id__models_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                connection_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    refresh_models_ai_connections__connection_id__models_refresh_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                connection_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    models_ai_models_get: {
        parameters: {
            query?: {
                connection_id?: string | null;
                provider?: components["schemas"]["ProviderType"] | null;
                task_type?: components["schemas"]["ModelTaskType"] | null;
                input_modality?: components["schemas"]["Modality"] | null;
                output_modality?: components["schemas"]["Modality"] | null;
                available_only?: boolean;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    model_ai_models__model_key__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                model_key: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    health_check_health_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
}
