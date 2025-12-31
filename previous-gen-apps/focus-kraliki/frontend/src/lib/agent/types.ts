/**
 * II-Agent TypeScript Types
 * Mirrors Pydantic models from ii-agent/src/ii_agent/server/models/messages.py
 * and ii-agent/src/ii_agent/core/event.py
 */

// Event Types from ii_agent/core/event.py
export enum EventType {
	CONNECTION_ESTABLISHED = 'connection_established',
	AGENT_INITIALIZED = 'agent_initialized',
	WORKSPACE_INFO = 'workspace_info',
	PROCESSING = 'processing',
	AGENT_THINKING = 'agent_thinking',
	TOOL_CALL = 'tool_call',
	TOOL_RESULT = 'tool_result',
	AGENT_RESPONSE = 'agent_response',
	AGENT_RESPONSE_INTERRUPTED = 'agent_response_interrupted',
	STREAM_COMPLETE = 'stream_complete',
	ERROR = 'error',
	SYSTEM = 'system',
	PONG = 'pong',
	UPLOAD_SUCCESS = 'upload_success',
	BROWSER_USE = 'browser_use',
	FILE_EDIT = 'file_edit',
	USER_MESSAGE = 'user_message',
	PROMPT_GENERATED = 'prompt_generated'
}

export interface RealtimeEvent {
	type: EventType;
	content: Record<string, any>;
}

// WebSocket Message Types from ii_agent/server/models/messages.py

export interface WebSocketMessage {
	type: string;
	content: Record<string, any>;
}

export interface FileInfo {
	path: string;
	content: string;
}

export interface UploadRequest {
	session_id: string;
	file: FileInfo;
}

export interface SessionInfo {
	id: string;
	workspace_dir: string;
	created_at: string;
	device_id: string;
	name?: string;
}

export interface SessionResponse {
	sessions: SessionInfo[];
}

export interface EventInfo {
	id: string;
	session_id: string;
	timestamp: string;
	event_type: string;
	event_payload: Record<string, any>;
	workspace_dir: string;
}

export interface EventResponse {
	events: EventInfo[];
}

export interface QueryContent {
	text?: string;
	resume?: boolean;
	files?: string[];
}

export interface InitAgentContent {
	model_name: string;
	tool_args?: Record<string, any>;
	thinking_tokens?: number;
}

export interface EnhancePromptContent {
	model_name: string;
	text?: string;
	files?: string[];
}

export interface EditQueryContent {
	text?: string;
	resume?: boolean;
	files?: string[];
}

export interface ReviewResultContent {
	user_input?: string;
}

// Message type helpers for constructing WebSocket messages

export interface InitAgentMessage extends WebSocketMessage {
	type: 'init_agent';
	content: InitAgentContent;
}

export interface QueryMessage extends WebSocketMessage {
	type: 'query';
	content: QueryContent;
}

export interface CancelMessage extends WebSocketMessage {
	type: 'cancel';
	content: Record<string, any>;
}

export interface EnhancePromptMessage extends WebSocketMessage {
	type: 'enhance_prompt';
	content: EnhancePromptContent;
}

export interface EditQueryMessage extends WebSocketMessage {
	type: 'edit_query';
	content: EditQueryContent;
}

export interface PingMessage extends WebSocketMessage {
	type: 'ping';
	content: Record<string, any>;
}

// Agent Session from Focus by Kraliki API
export interface AgentSessionResponse {
	agentToken: string;
	sessionUuid: string;
}

// UI State types

export interface AgentConfig {
	model_name: string;
	enable_focus_tools: boolean;
	enable_reviewer: boolean;
	thinking_tokens?: number;
}

export interface ConnectionState {
	isConnected: boolean;
	isConnecting: boolean;
	isAgentInitialized: boolean;
	error: string | null;
	sessionUuid: string | null;
	agentToken: string | null;
}

export interface EventLogEntry {
	id: string;
	timestamp: Date;
	type: EventType;
	content: Record<string, any>;
	formattedContent?: string;
}
