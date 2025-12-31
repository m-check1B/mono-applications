import { browser } from '$app/environment';
import { writable, get, type Readable } from 'svelte/store';
import { float32ToInt16 } from '$lib/utils/pcm';

export type AudioManagerStatus = 'idle' | 'requesting-mic' | 'ready' | 'recording' | 'playing' | 'error';

export interface AudioManagerState {
	status: AudioManagerStatus;
	message?: string;
	error?: string;
	lastPlaybackAt?: number;
}

export interface AudioManager extends Readable<AudioManagerState> {
	startMicrophone(): Promise<{ success: boolean; error?: string }>;
	stop(): void;
	playBase64Audio(chunk: string, mimeType?: string | null, channels?: number): Promise<void>;
	cleanup(): Promise<void>;
	setMessage(message: string): void;
	sendCapturedFrame(callback: (buffer: Int16Array) => void): void;
	getState(): AudioManagerState;
}

export function createAudioManager(): AudioManager {
	const state = writable<AudioManagerState>({ status: 'idle' });

	if (!browser) {
		return {
			subscribe: state.subscribe,
			async startMicrophone() {
				state.set({ status: 'error', error: 'Audio manager unavailable outside browser.' });
				return { success: false, error: 'Audio manager unavailable outside browser.' };
			},
			stop() {
				state.set({ status: 'idle' });
			},
			async playBase64Audio() {
				// no-op on server
			},
			async cleanup() {
				state.set({ status: 'idle' });
			},
			setMessage(message: string) {
				state.update((prev) => ({ ...prev, message }));
			},
			sendCapturedFrame() {
				// no-op
			},
			getState() {
				return get(state);
			}
		};
	}

	let inputContext: AudioContext | null = null;
	let outputContext: AudioContext | null = null;
	let mediaStream: MediaStream | null = null;
	let sourceNode: MediaStreamAudioSourceNode | null = null;
let gainNode: GainNode | null = null;
let workletNode: AudioWorkletNode | null = null;
let workletCallback: ((buffer: Int16Array) => void) | null = null;
const audioSources = new Set<AudioBufferSourceNode>();
let nextStartTime = 0;

	function setState(update: Partial<AudioManagerState>) {
		state.update((prev) => ({ ...prev, ...update }));
	}

	function base64ToUint8Array(base64: string): Uint8Array {
		const binaryString = atob(base64);
		const length = binaryString.length;
		const bytes = new Uint8Array(length);
		for (let i = 0; i < length; i += 1) {
			bytes[i] = binaryString.charCodeAt(i);
		}
		return bytes;
	}

	function parseSampleRate(mimeType?: string | null): number {
		if (!mimeType) return 24000;
		const match = mimeType.match(/rate=(\d+)/i);
		if (match) {
			const rate = Number(match[1]);
			if (!Number.isNaN(rate) && rate > 0) {
				return rate;
			}
		}
		return 24000;
	}

	function parseChannels(mimeType?: string | null, fallback = 1): number {
		if (!mimeType) return fallback;
		const match = mimeType.match(/channels=(\d+)/i);
		if (match) {
			const channels = Number(match[1]);
			if (!Number.isNaN(channels) && channels > 0) {
				return channels;
			}
		}
		return fallback;
	}

	function ensureAudioContext(): { input: AudioContext; output: AudioContext } {
		const Ctor = window.AudioContext || (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
		if (!Ctor) {
			throw new Error('Web Audio API is not supported in this browser');
		}

		if (!inputContext || inputContext.state === 'closed') {
			inputContext = new Ctor();
		}
		if (!outputContext || outputContext.state === 'closed') {
			outputContext = new Ctor();
		}
		return { input: inputContext, output: outputContext };
	}

	async function resumeContexts() {
		if (inputContext && inputContext.state === 'suspended') {
			await inputContext.resume();
		}
		if (outputContext && outputContext.state === 'suspended') {
			await outputContext.resume();
		}
	}

	function ensureGainNode(ctx: AudioContext) {
		if (!gainNode) {
			gainNode = ctx.createGain();
			gainNode.gain.value = 1.0;
			gainNode.connect(ctx.destination);
		}
		return gainNode;
	}

	async function ensureAudioWorklet(ctx: AudioContext) {
		if (workletNode) return workletNode;
		try {
			await ctx.audioWorklet.addModule('/worklets/audio-processor.js');
			workletNode = new AudioWorkletNode(ctx, 'audio-processor');
			workletNode.port.onmessage = (event) => {
				if (event.data?.type === 'audioData' && workletCallback) {
					const buffer = event.data.buffer as Int16Array;
					workletCallback(buffer);
				}
			};
			return workletNode;
		} catch (error) {
			setState({ status: 'error', error: 'AudioWorklet not available.' });
			throw error;
		}
	}

	function decodePcmToBuffer(bytes: Uint8Array, ctx: AudioContext, sampleRate: number, channels: number): AudioBuffer {
		const frameCount = Math.floor(bytes.length / 2 / channels);
		const buffer = ctx.createBuffer(channels, frameCount, sampleRate);
		const int16View = new Int16Array(bytes.buffer, bytes.byteOffset, frameCount * channels);

		for (let channel = 0; channel < channels; channel += 1) {
			const channelData = buffer.getChannelData(channel);
			for (let i = 0; i < frameCount; i += 1) {
				const sampleIndex = i * channels + channel;
				channelData[i] = int16View[sampleIndex] / 32768;
			}
		}

		return buffer;
	}

	async function startMicrophone(): Promise<{ success: boolean; error?: string }> {
		if (!browser) {
			return { success: false, error: 'Microphone unavailable outside browser.' };
		}

		if (!navigator.mediaDevices?.getUserMedia) {
			setState({ status: 'error', error: 'Microphone access is not supported in this environment.' });
			return { success: false, error: 'Microphone access is not supported.' };
		}

		try {
			setState({ status: 'requesting-mic', error: undefined, message: 'Requesting microphone access…' });

			const stream = await navigator.mediaDevices.getUserMedia({
				audio: {
					sampleRate: 16000,
					channelCount: 1,
					echoCancellation: true,
					noiseSuppression: false,
					autoGainControl: false
				}
			});

			mediaStream = stream;

			const { input, output } = ensureAudioContext();
			await resumeContexts();

			sourceNode = input.createMediaStreamSource(stream);

			// Ensure output gain node exists for playback
			ensureGainNode(output);
			await ensureAudioWorklet(input);
			workletNode?.port.postMessage({ type: 'config', sampleRate: input.sampleRate });
			sourceNode.connect(workletNode!);

			nextStartTime = output.currentTime;

			setState({ status: 'recording', message: 'Microphone capture active.' });
			return { success: true };
		} catch (error) {
			console.error('Failed to start microphone', error);
			const message = error instanceof Error ? error.message : 'Unknown microphone error';
			setState({ status: 'error', error: message });
			return { success: false, error: message };
		}
	}

	function stopMicrophone() {
		if (mediaStream) {
			mediaStream.getTracks().forEach((track) => track.stop());
			mediaStream = null;
		}

		if (sourceNode) {
			sourceNode.disconnect();
			sourceNode = null;
		}

		if (workletNode) {
			try {
				workletNode.port.postMessage({ type: 'stop' });
			} catch (error) {
				console.warn('Failed to notify worklet stop', error);
			}
			workletNode.disconnect();
			workletNode = null;
		}

		audioSources.forEach((source) => {
			try {
				source.stop();
			} catch (error) {
				console.warn('Error stopping audio source', error);
			}
		});
		audioSources.clear();
		nextStartTime = outputContext ? outputContext.currentTime : 0;

		setState({ status: 'ready', message: 'Microphone stopped.' });
	}

	async function cleanupContexts() {
		stopMicrophone();

		if (gainNode) {
			gainNode.disconnect();
			gainNode = null;
		}

		if (inputContext && inputContext.state !== 'closed') {
			await inputContext.close();
		}
		if (outputContext && outputContext.state !== 'closed') {
			await outputContext.close();
		}

		inputContext = null;
		outputContext = null;
		nextStartTime = 0;

		setState({ status: 'idle', message: undefined, error: undefined });
	}

	async function playBase64Audio(chunk: string, mimeType?: string | null, channels = 1) {
		if (!browser) return;
		if (!chunk) return;

		try {
			const { output } = ensureAudioContext();
			await resumeContexts();
			const gain = ensureGainNode(output);

			const bytes = base64ToUint8Array(chunk);
			const sampleRate = parseSampleRate(mimeType);
			const resolvedChannels = parseChannels(mimeType, channels);
			const buffer = decodePcmToBuffer(bytes, output, sampleRate, resolvedChannels);

			const source = output.createBufferSource();
			source.buffer = buffer;
			source.connect(gain);

			const startTime = Math.max(nextStartTime, output.currentTime);
			source.start(startTime);
			nextStartTime = startTime + buffer.duration;

			source.addEventListener('ended', () => {
				audioSources.delete(source);
			});
			audioSources.add(source);

			setState({
				status: get(state).status === 'error' ? 'ready' : get(state).status,
				message: `Playing audio chunk (${buffer.duration.toFixed(2)}s)` ,
				lastPlaybackAt: Date.now(),
				error: undefined
			});
		} catch (error) {
			console.error('Failed to play audio chunk', error);
			const message = error instanceof Error ? error.message : 'Unable to play audio chunk';
			setState({ status: 'error', error: message });
		}
	}

	return {
		subscribe: state.subscribe,
		startMicrophone,
		stop: stopMicrophone,
		playBase64Audio,
		cleanup: cleanupContexts,
		setMessage(message: string) {
			setState({ message });
		},
		sendCapturedFrame(callback: (buffer: Int16Array) => void) {
			workletCallback = callback;
		},
		getState() {
			return get(state);
		}
	};
}
