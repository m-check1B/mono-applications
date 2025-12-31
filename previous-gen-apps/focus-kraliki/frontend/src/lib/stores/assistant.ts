/**
 * Assistant Store - Unified state management for AI-First Command Center
 * Manages conversation, workflows, execution feed, and II-Agent integration
 */

import { writable, derived, get } from 'svelte/store';
import type { Writable, Readable } from 'svelte/store';
import type { RealtimeEvent, EventType } from '$lib/agent/types';

// ========== Core Types ==========

export interface AssistantMessage {
	id: string;
	role: 'user' | 'assistant' | 'system';
	content: string;
	timestamp: Date;
	source: 'text' | 'voice' | 'ii-agent' | 'brain';
	metadata?: {
		model?: string;
		provider?: string;
		telemetryId?: string;
		workflowId?: string;
		thinking?: string;
		toolCalls?: ToolCall[];
	};
}

export interface ToolCall {
	id: string;
	name: string;
	arguments: Record<string, any>;
	result?: any;
	status: 'pending' | 'running' | 'completed' | 'error';
	timestamp: Date;
}

export interface WorkflowPlan {
	id: string;
	telemetryId?: string;
	sessionId?: string;
	mainTask?: {
		title: string;
		description?: string;
	};
	workflow?: WorkflowStep[];
	artifacts?: WorkflowArtifact[];
	confidence?: number;
	decisionStatus?: 'pending' | 'approved' | 'revise' | 'rejected';
	decisionAt?: string;
	timestamp: Date;
	messageId?: string; // Reference to triggering message
}

export interface WorkflowStep {
	step: number;
	action: string;
	estimatedMinutes?: number;
	status?: 'pending' | 'running' | 'completed' | 'error';
	result?: any;
}

export interface WorkflowArtifact {
	id: string;
	type: string;
	label?: string;
	title?: string;
	name?: string;
	summary?: string;
	description?: string;
	url?: string;
	data?: any;
}

export interface ExecutionEntry {
	id: string;
	type: 'task' | 'knowledge' | 'event' | 'automation';
	title: string;
	status: string;
	meta?: string;
	typeLabel?: string;
	content?: string;
	timestamp: Date;
	sourceMessageId?: string;
	sourceWorkflowId?: string;
}

export interface ComposerState {
	isRecording: boolean;
	isProcessing: boolean;
	provider: string;
	mode: 'deterministic' | 'orchestrated' | 'ii-agent';
	model?: string;
	useOrchestrator: boolean;
}

export interface IIAgentState {
	isConnected: boolean;
	isInitialized: boolean;
	sessionUuid: string | null;
	agentToken: string | null;
	currentModel: string | null;
	isProcessing: boolean;
	error: string | null;
	eventLog: IIAgentEvent[];
}

export interface IIAgentEvent {
	id: string;
	type: EventType;
	content: Record<string, any>;
	timestamp: Date;
	formattedContent?: string;
}

export interface AssistantState {
	sessionId: string | null;
	messages: AssistantMessage[];
	workflows: Record<string, WorkflowPlan>;
	executionFeed: ExecutionEntry[];
	composerState: ComposerState;
	iiAgentState: IIAgentState;
    currentAction: string | null;
	drawerState: {
		workflowDrawerOpen: boolean;
		executionDrawerOpen: boolean;
		selectedWorkflowId: string | null;
		selectedExecutionId: string | null;
	};
}

// ========== Initial State ==========

const initialComposerState: ComposerState = {
	isRecording: false,
	isProcessing: false,
	provider: 'gemini-native',
	mode: 'ii-agent',
	model: 'google/gemini-3-flash-preview',
	useOrchestrator: false
};

const initialIIAgentState: IIAgentState = {
	isConnected: false,
	isInitialized: false,
	sessionUuid: null,
	agentToken: null,
	currentModel: null,
	isProcessing: false,
	error: null,
	eventLog: []
};

const initialState: AssistantState = {
	sessionId: null,
	messages: [],
	workflows: {},
	executionFeed: [],
	composerState: initialComposerState,
	iiAgentState: initialIIAgentState,
    currentAction: null,
	drawerState: {
		workflowDrawerOpen: false,
		executionDrawerOpen: false,
		selectedWorkflowId: null,
		selectedExecutionId: null
	}
};

// ========== Store Creation ==========

function createAssistantStore() {
	const { subscribe, set, update }: Writable<AssistantState> = writable(initialState);

	return {
		subscribe,

		// ========== Session Management ==========

		initSession: (sessionId?: string) => {
			update(state => ({
				...state,
				sessionId: sessionId || crypto.randomUUID?.() || String(Date.now())
			}));
		},

        setCurrentAction: (action: string | null) => {
            update(state => ({
                ...state,
                currentAction: action
            }));
        },

		clearSession: () => {
			set(initialState);
		},

		// ========== Message Management ==========

		addMessage: (message: Omit<AssistantMessage, 'id' | 'timestamp'>) => {
			const newMessage: AssistantMessage = {
				...message,
				id: crypto.randomUUID?.() || String(Date.now()),
				timestamp: new Date()
			};

			update(state => ({
				...state,
				messages: [...state.messages, newMessage]
			}));

			return newMessage;
		},

		updateMessage: (messageId: string, updates: Partial<AssistantMessage>) => {
			update(state => ({
				...state,
				messages: state.messages.map(msg =>
					msg.id === messageId ? { ...msg, ...updates } : msg
				)
			}));
		},

		deleteMessage: (messageId: string) => {
			update(state => ({
				...state,
				messages: state.messages.filter(msg => msg.id !== messageId)
			}));
		},

		clearMessages: () => {
			update(state => ({
				...state,
				messages: []
			}));
		},

		// ========== Workflow Management ==========

		addWorkflow: (workflow: Omit<WorkflowPlan, 'id' | 'timestamp'>) => {
			const newWorkflow: WorkflowPlan = {
				...workflow,
				id: workflow.telemetryId || crypto.randomUUID?.() || String(Date.now()),
				timestamp: new Date()
			};

			update(state => ({
				...state,
				workflows: {
					...state.workflows,
					[newWorkflow.id]: newWorkflow
				}
			}));

			return newWorkflow;
		},

		updateWorkflow: (workflowId: string, updates: Partial<WorkflowPlan>) => {
			update(state => ({
				...state,
				workflows: {
					...state.workflows,
					[workflowId]: {
						...state.workflows[workflowId],
						...updates
					}
				}
			}));
		},

		deleteWorkflow: (workflowId: string) => {
			update(state => {
				const { [workflowId]: _, ...rest } = state.workflows;
				return {
					...state,
					workflows: rest
				};
			});
		},

		updateWorkflowDecision: (workflowId: string, status: WorkflowPlan['decisionStatus']) => {
			update(state => ({
				...state,
				workflows: {
					...state.workflows,
					[workflowId]: {
						...state.workflows[workflowId],
						decisionStatus: status,
						decisionAt: new Date().toISOString()
					}
				}
			}));
		},

		// ========== Execution Feed Management ==========

		addExecutionEntry: (entry: Omit<ExecutionEntry, 'id' | 'timestamp'>) => {
			const newEntry: ExecutionEntry = {
				...entry,
				id: crypto.randomUUID?.() || String(Date.now()),
				timestamp: new Date()
			};

			update(state => ({
				...state,
				executionFeed: [newEntry, ...state.executionFeed]
			}));

			return newEntry;
		},

		updateExecutionEntry: (entryId: string, updates: Partial<ExecutionEntry>) => {
			update(state => ({
				...state,
				executionFeed: state.executionFeed.map(entry =>
					entry.id === entryId ? { ...entry, ...updates } : entry
				)
			}));
		},

		deleteExecutionEntry: (entryId: string) => {
			update(state => ({
				...state,
				executionFeed: state.executionFeed.filter(entry => entry.id !== entryId)
			}));
		},

		setExecutionFeed: (entries: ExecutionEntry[]) => {
			update(state => ({
				...state,
				executionFeed: entries
			}));
		},

		clearExecutionFeed: () => {
			update(state => ({
				...state,
				executionFeed: []
			}));
		},

		// ========== Composer State Management ==========

		setComposerState: (updates: Partial<ComposerState>) => {
			update(state => ({
				...state,
				composerState: {
					...state.composerState,
					...updates
				}
			}));
		},

		setRecording: (isRecording: boolean) => {
			update(state => ({
				...state,
				composerState: {
					...state.composerState,
					isRecording
				}
			}));
		},

		setProcessing: (isProcessing: boolean) => {
			update(state => ({
				...state,
				composerState: {
					...state.composerState,
					isProcessing
				}
			}));
		},

		setMode: (mode: ComposerState['mode']) => {
			update(state => ({
				...state,
				composerState: {
					...state.composerState,
					mode
				}
			}));
		},

		// ========== II-Agent State Management ==========

		setIIAgentConnection: (isConnected: boolean, sessionUuid?: string, agentToken?: string) => {
			update(state => ({
				...state,
				iiAgentState: {
					...state.iiAgentState,
					isConnected,
					sessionUuid: sessionUuid || state.iiAgentState.sessionUuid,
					agentToken: agentToken || state.iiAgentState.agentToken,
					error: isConnected ? null : state.iiAgentState.error
				}
			}));
		},

		setIIAgentInitialized: (isInitialized: boolean, model?: string) => {
			update(state => ({
				...state,
				iiAgentState: {
					...state.iiAgentState,
					isInitialized,
					currentModel: model || state.iiAgentState.currentModel
				}
			}));
		},

		setIIAgentProcessing: (isProcessing: boolean) => {
			update(state => ({
				...state,
				iiAgentState: {
					...state.iiAgentState,
					isProcessing
				}
			}));
		},

		setIIAgentError: (error: string | null) => {
			update(state => ({
				...state,
				iiAgentState: {
					...state.iiAgentState,
					error
				}
			}));
		},

		addIIAgentEvent: (event: RealtimeEvent) => {
			const newEvent: IIAgentEvent = {
				id: crypto.randomUUID?.() || String(Date.now()),
				type: event.type,
				content: event.content,
				timestamp: new Date(),
				formattedContent: formatIIAgentEvent(event)
			};

			update(state => ({
				...state,
				iiAgentState: {
					...state.iiAgentState,
					eventLog: [...state.iiAgentState.eventLog, newEvent]
				}
			}));

			return newEvent;
		},

		clearIIAgentEvents: () => {
			update(state => ({
				...state,
				iiAgentState: {
					...state.iiAgentState,
					eventLog: []
				}
			}));
		},

		// ========== Drawer State Management ==========

		openWorkflowDrawer: (workflowId: string) => {
			update(state => ({
				...state,
				drawerState: {
					...state.drawerState,
					workflowDrawerOpen: true,
					selectedWorkflowId: workflowId
				}
			}));
		},

		closeWorkflowDrawer: () => {
			update(state => ({
				...state,
				drawerState: {
					...state.drawerState,
					workflowDrawerOpen: false,
					selectedWorkflowId: null
				}
			}));
		},

		openExecutionDrawer: (executionId: string) => {
			update(state => ({
				...state,
				drawerState: {
					...state.drawerState,
					executionDrawerOpen: true,
					selectedExecutionId: executionId
				}
			}));
		},

		closeExecutionDrawer: () => {
			update(state => ({
				...state,
				drawerState: {
					...state.drawerState,
					executionDrawerOpen: false,
					selectedExecutionId: null
				}
			}));
		},

		// ========== Utility Methods ==========

		getState: (): AssistantState => {
			return get({ subscribe });
		}
	};
}

// ========== Helper Functions ==========

function formatIIAgentEvent(event: RealtimeEvent): string {
	switch (event.type) {
		case 'agent_response':
			return event.content.text || '';
		case 'agent_thinking':
			return `Thinking: ${event.content.thinking || '...'}`;
		case 'tool_call':
			return `Tool: ${event.content.tool_name || 'unknown'}`;
		case 'tool_result':
			return `Result: ${JSON.stringify(event.content.result || {}).substring(0, 100)}...`;
		case 'error':
			return `Error: ${event.content.error || event.content.message || 'Unknown error'}`;
		case 'system':
			return event.content.message || event.content.text || 'System event';
		default:
			return JSON.stringify(event.content);
	}
}

// ========== Derived Stores ==========

export const assistantStore = createAssistantStore();

// Derived store for active workflow
export const activeWorkflow: Readable<WorkflowPlan | null> = derived(
	assistantStore,
	$state => {
		if (!$state.drawerState.selectedWorkflowId) return null;
		return $state.workflows[$state.drawerState.selectedWorkflowId] || null;
	}
);

// Derived store for active execution entry
export const activeExecution: Readable<ExecutionEntry | null> = derived(
	assistantStore,
	$state => {
		if (!$state.drawerState.selectedExecutionId) return null;
		return $state.executionFeed.find(e => e.id === $state.drawerState.selectedExecutionId) || null;
	}
);

// Derived store for latest workflow
export const latestWorkflow: Readable<WorkflowPlan | null> = derived(
	assistantStore,
	$state => {
		const workflows = Object.values($state.workflows);
		if (workflows.length === 0) return null;
		return workflows.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())[0];
	}
);

// Derived store for recent messages
export const recentMessages: Readable<AssistantMessage[]> = derived(
	assistantStore,
	$state => $state.messages.slice(-20)
);

// Derived store for II-Agent connection status
export const iiAgentConnected: Readable<boolean> = derived(
	assistantStore,
	$state => $state.iiAgentState.isConnected && $state.iiAgentState.isInitialized
);

// Derived store for processing state
export const isProcessing: Readable<boolean> = derived(
	assistantStore,
	$state => $state.composerState.isProcessing || $state.iiAgentState.isProcessing
);
