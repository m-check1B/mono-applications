/// <reference types="vite/client" />

interface ImportMetaEnv {
	readonly PUBLIC_API_URL: string;
	readonly PUBLIC_VOICE_PROVIDER?: "gemini-native" | "openai-realtime";
	readonly PUBLIC_ENABLE_VOICE?: string;
	readonly PUBLIC_II_AGENT_WS_URL?: string;
	readonly PUBLIC_GOOGLE_REDIRECT_URI?: string;
}

interface ImportMeta {
	readonly env: ImportMetaEnv;
}
