/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string;
  readonly VITE_REQUEST_TIMEOUT_MS?: string;
  readonly VITE_UPLOAD_TIMEOUT_MS?: string;
  readonly VITE_CHAT_TIMEOUT_MS?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
