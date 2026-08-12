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
        /**
         * Chat Stream Endpoint
         * @description 流式聊天接口
         */
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
        patch?: never;
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
    "/api-keys/": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Create Api Key
         * @description 创建API key
         */
        post: operations["create_api_key_api_keys__post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api-keys/user/{user_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Get User Api Keys
         * @description 获取用户的所有API key
         */
        get: operations["get_user_api_keys_api_keys_user__user_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api-keys/{api_key_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        /**
         * Update Api Key
         * @description 更新属于当前用户的 API Key，响应中不会返回密钥正文。
         */
        put: operations["update_api_key_api_keys__api_key_id__put"];
        post?: never;
        /**
         * Delete Api Key
         * @description 删除API key
         */
        delete: operations["delete_api_key_api_keys__api_key_id__delete"];
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
    "/models": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Get Models
         * @description 返回可用模型列表，分为本地模型和在线模型
         */
        get: operations["get_models_models_get"];
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
        /** ApiKeyCreate */
        ApiKeyCreate: {
            /** User Id */
            user_id?: number | null;
            /** Provider */
            provider: string;
            /** Api Key */
            api_key: string;
            /** Model Name */
            model_name?: string | null;
        };
        /** ApiKeyListResponse */
        ApiKeyListResponse: {
            /** Api Keys */
            api_keys: components["schemas"]["ApiKeyResponse"][];
        };
        /** ApiKeyResponse */
        ApiKeyResponse: {
            /** Id */
            id: number;
            /** User Id */
            user_id: number;
            /** Provider */
            provider: string;
            /** Model Name */
            model_name: string | null;
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
        /** ApiKeyUpdate */
        ApiKeyUpdate: {
            /** Api Key */
            api_key: string;
            /** Model Name */
            model_name?: string | null;
            /**
             * Is Active
             * @default true
             */
            is_active: boolean;
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
        /** ChatHistoryResponse */
        ChatHistoryResponse: {
            /** Conversation Id */
            conversation_id: number;
            /** Messages */
            messages: components["schemas"]["ChatMessageResponse"][];
        };
        /** ChatMessageResponse */
        ChatMessageResponse: {
            /** Role */
            role: string;
            /** Content */
            content: string;
        };
        /** ChatRequest */
        ChatRequest: {
            /** User Id */
            user_id?: number | null;
            /** Conversation Id */
            conversation_id: number;
            /** Message */
            message: string;
            /** Model */
            model: string;
            /**
             * Mode
             * @default chat
             */
            mode: string;
            /**
             * Use Rag
             * @default false
             */
            use_rag: boolean;
            /**
             * Use Wiki
             * @default false
             */
            use_wiki: boolean;
            /** Knowledge Base Id */
            knowledge_base_id?: number | null;
            /**
             * Stream
             * @default true
             */
            stream: boolean;
            /**
             * Regenerate
             * @default false
             */
            regenerate: boolean;
            /**
             * Chain Type
             * @default stuff
             */
            chain_type: string;
            /**
             * Prompt Name
             * @default chat_default
             */
            prompt_name: string;
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
                "application/json": components["schemas"]["ChatRequest"];
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
                    "application/json": components["schemas"]["ChatHistoryResponse"];
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
    create_api_key_api_keys__post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ApiKeyCreate"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiKeyResponse"];
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
    get_user_api_keys_api_keys_user__user_id__get: {
        parameters: {
            query?: {
                include_inactive?: boolean;
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
                    "application/json": components["schemas"]["ApiKeyListResponse"];
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
    update_api_key_api_keys__api_key_id__put: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                api_key_id: number;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ApiKeyUpdate"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApiKeyResponse"];
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
    delete_api_key_api_keys__api_key_id__delete: {
        parameters: {
            query?: {
                user_id?: number | null;
            };
            header?: never;
            path: {
                api_key_id: number;
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
    get_models_models_get: {
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
