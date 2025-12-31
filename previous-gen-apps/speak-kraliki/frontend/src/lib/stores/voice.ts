/**
 * Speak by Kraliki - Voice Conversation Store
 */

import { writable, derived } from 'svelte/store';
import { voice } from '$api/client';

interface TranscriptTurn {
  role: 'ai' | 'user';
  content: string;
  timestamp: string;
  redacted?: boolean;
}

interface VoiceState {
  status: 'idle' | 'connecting' | 'consent' | 'active' | 'completed' | 'error';
  mode: 'voice' | 'text';
  transcript: TranscriptTurn[];
  currentMessage: string;
  isRecording: boolean;
  isProcessing: boolean;
  error: string | null;
  wsConnection: WebSocket | null;
  conversationId: string | null;
  reachMode: boolean;
  reachSessionId: string | null;
  startedAt: number | null;
  magicToken: string | null;
}

const initialState: VoiceState = {
  status: 'idle',
  mode: 'voice',
  transcript: [],
  currentMessage: '',
  isRecording: false,
  isProcessing: false,
  error: null,
  wsConnection: null,
  conversationId: null,
  reachMode: false,
  reachSessionId: null,
  startedAt: null,
  magicToken: null,
};

function createVoiceStore() {
  const { subscribe, set, update } = writable<VoiceState>(initialState);

  const resolveWebsocketUrl = (rawUrl: string): string => {
    if (rawUrl.startsWith('ws://') || rawUrl.startsWith('wss://')) {
      return rawUrl;
    }

    if (rawUrl.startsWith('http://') || rawUrl.startsWith('https://')) {
      const wsScheme = rawUrl.startsWith('https://') ? 'wss' : 'ws';
      return rawUrl.replace(/^https?:\/\//, `${wsScheme}://`);
    }

    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    return `${protocol}://${window.location.host}${rawUrl}`;
  };

  return {
    subscribe,

    connect: async (token: string) => {
      update((state) => ({
        ...state,
        status: 'connecting',
        magicToken: token,
      }));

      try {
        const startResponse = await voice.start(token, initialState.mode);
        const reachMode = startResponse.reach === true;
        const wsUrl = resolveWebsocketUrl(startResponse.websocket_url);
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
          update((state) => ({
            ...state,
            status: 'active',
            wsConnection: ws,
            reachMode,
            conversationId: startResponse.conversation_id,
            reachSessionId: startResponse.reach_session_id || null,
            startedAt: Date.now(),
          }));
        };

        ws.onmessage = (event) => {
          const data = JSON.parse(event.data);

          if (data.type === 'error') {
            update((state) => ({
              ...state,
              status: 'error',
              error: data.message || data.error || data.data?.error || 'Connection error',
            }));
            return;
          }

          if (!reachMode && data.type === 'ai_message') {
            update((state) => ({
              ...state,
              transcript: [
                ...state.transcript,
                {
                  role: 'ai',
                  content: data.content,
                  timestamp: new Date().toISOString(),
                },
              ],
              isProcessing: false,
            }));
          }

          if (reachMode && data.type === 'text.output') {
            update((state) => ({
              ...state,
              transcript: [
                ...state.transcript,
                {
                  role: 'ai',
                  content: data.data?.text || '',
                  timestamp: new Date().toISOString(),
                },
              ],
              isProcessing: false,
            }));
          }

          if (!reachMode && data.type === 'completed') {
            update((state) => ({
              ...state,
              status: 'completed',
            }));
          }

          if (!reachMode && data.type === 'mode_changed') {
            update((state) => ({
              ...state,
              mode: data.mode,
            }));
          }
        };

        ws.onerror = () => {
          update((state) => ({
            ...state,
            status: 'error',
            error: 'Connection error',
          }));
        };

        ws.onclose = () => {
          update((state) => ({
            ...state,
            wsConnection: null,
          }));
        };

        update((state) => ({
          ...state,
          wsConnection: ws,
        }));
      } catch (err: any) {
        update((state) => ({
          ...state,
          status: 'error',
          error: err?.message || 'Failed to start voice session',
        }));
      }
    },

    sendMessage: (content: string, type: 'text' | 'audio' = 'text') => {
      update((state) => {
        if (state.wsConnection?.readyState === WebSocket.OPEN) {
          state.wsConnection.send(JSON.stringify({ type, content }));

          return {
            ...state,
            transcript: [
              ...state.transcript,
              {
                role: 'user',
                content,
                timestamp: new Date().toISOString(),
              },
            ],
            currentMessage: '',
            isProcessing: true,
          };
        }
        return state;
      });
    },

    endConversation: async () => {
      let snapshot: VoiceState | undefined;

      update((state) => {
        snapshot = state;
        if (state.wsConnection?.readyState === WebSocket.OPEN) {
          if (!state.reachMode) {
            state.wsConnection.send(JSON.stringify({ type: 'end' }));
          }
          state.wsConnection.close();
        }
        return state;
      });

      if (snapshot && snapshot.reachMode && snapshot.magicToken) {
        const durationSeconds = snapshot.startedAt
          ? Math.max(0, Math.floor((Date.now() - snapshot.startedAt) / 1000))
          : undefined;

        try {
          await voice.complete(snapshot.magicToken, snapshot.transcript, durationSeconds);
        } catch {
          // Best-effort completion for Reach sessions
        }
      }

      update((state) => ({ ...state, status: 'completed' }));
    },

    switchToText: (reason = 'user_requested') => {
      update((state) => {
        if (!state.reachMode && state.wsConnection?.readyState === WebSocket.OPEN) {
          state.wsConnection.send(
            JSON.stringify({ type: 'fallback', reason })
          );
        }
        return { ...state, mode: 'text' };
      });
    },

    setRecording: (isRecording: boolean) => {
      update((state) => ({ ...state, isRecording }));
    },

    setCurrentMessage: (message: string) => {
      update((state) => ({ ...state, currentMessage: message }));
    },

    setConsent: () => {
      update((state) => ({ ...state, status: 'consent' }));
    },

    reset: () => {
      update((state) => {
        state.wsConnection?.close();
        return initialState;
      });
    },
  };
}

export const voiceStore = createVoiceStore();

// Derived
export const isVoiceActive = derived(
  voiceStore,
  ($voice) => $voice.status === 'active'
);

export const conversationTranscript = derived(
  voiceStore,
  ($voice) => $voice.transcript
);
