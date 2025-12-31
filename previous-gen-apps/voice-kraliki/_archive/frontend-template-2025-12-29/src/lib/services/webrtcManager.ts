/**
 * WebRTC Manager
 * 
 * Handles WebRTC peer connections for real-time audio communication:
 * - Peer connection management
 * - Audio stream handling
 * - Connection quality monitoring
 * - Automatic reconnection
 * - Provider switching support
 */

import { browser } from '$app/environment';
import { writable, type Readable, get } from 'svelte/store';
import { createAudioManager, type AudioManager } from './audioManager';
import { logger } from '$lib/utils/logger';

export type WebRTCConnectionState = 
	| 'idle'
	| 'connecting' 
	| 'connected'
	| 'disconnected'
	| 'reconnecting'
	| 'failed';

export interface WebRTCStats {
	connectionState: WebRTCConnectionState;
	latency: number;
	packetLoss: number;
	audioLevel: number;
	bitrate: number;
	lastUpdate: number;
}

export interface WebRTCConfig {
	iceServers?: RTCIceServer[];
	enableAudio?: boolean;
	enableVideo?: boolean;
	autoReconnect?: boolean;
	reconnectInterval?: number;
	maxReconnectAttempts?: number;
}

export interface WebRTCManager extends Readable<WebRTCStats> {
	connect(signalingUrl: string): Promise<void>;
	disconnect(): Promise<void>;
	switchProvider(newProvider: string): Promise<void>;
	getConnectionState(): WebRTCConnectionState;
	getStats(): Promise<RTCStatsReport | null>;
	muteAudio(muted: boolean): void;
	sendAudioChunk(chunk: ArrayBuffer): void;
	startScreenShare(): Promise<MediaStream>;
	stopScreenShare(): void;
	getScreenShareStream(): MediaStream | null;
	isScreenSharing(): boolean;
	cleanup(): Promise<void>;
}

export function createWebRTCManager(config: WebRTCConfig = {}): WebRTCManager {
	const defaultConfig: Required<WebRTCConfig> = {
		iceServers: [
			{ urls: 'stun:stun.l.google.com:19302' },
			{ urls: 'stun:stun1.l.google.com:19302' }
		],
		enableAudio: true,
		enableVideo: false,
		autoReconnect: true,
		reconnectInterval: 3000,
		maxReconnectAttempts: 5
	};

	const finalConfig = { ...defaultConfig, ...config };

	// State management
	const stats = writable<WebRTCStats>({
		connectionState: 'idle',
		latency: 0,
		packetLoss: 0,
		audioLevel: 0,
		bitrate: 0,
		lastUpdate: Date.now()
	});

	// WebRTC components
	let peerConnection: RTCPeerConnection | null = null;
	let localStream: MediaStream | null = null;
	let remoteStream: MediaStream | null = null;
	let signalingSocket: WebSocket | null = null;

	// Audio management
	const audioManager = createAudioManager();
	let audioContext: AudioContext | null = null;
	let analyser: AnalyserNode | null = null;
	let audioLevelInterval: ReturnType<typeof setInterval> | null = null;

	// Screen sharing state
	let screenStream: MediaStream | null = null;
	let screenTrack: MediaStreamTrack | null = null;

	// Reconnection state
	let reconnectAttempts = 0;
	let reconnectTimeout: ReturnType<typeof setTimeout> | null = null;
	let currentSignalingUrl = '';

	function updateStats(updates: Partial<WebRTCStats>) {
		stats.update(prev => ({
			...prev,
			...updates,
			lastUpdate: Date.now()
		}));
	}

	function updateConnectionState(state: WebRTCConnectionState) {
		updateStats({ connectionState: state });
		logger.info('WebRTC connection state updated', { state });
	}

	async function initializePeerConnection(): Promise<RTCPeerConnection> {
		if (!browser) {
			throw new Error('WebRTC not available outside browser');
		}

		const pc = new RTCPeerConnection({
			iceServers: finalConfig.iceServers
		});

		// Handle connection state changes
		pc.addEventListener('connectionstatechange', () => {
			switch (pc.connectionState) {
				case 'connected':
					updateConnectionState('connected');
					reconnectAttempts = 0;
					break;
				case 'disconnected':
					updateConnectionState('disconnected');
					if (finalConfig.autoReconnect) {
						scheduleReconnect();
					}
					break;
				case 'failed':
					updateConnectionState('failed');
					break;
				case 'connecting':
					updateConnectionState('connecting');
					break;
			}
		});

		// Handle ICE connection state
		pc.addEventListener('iceconnectionstatechange', () => {
			logger.debug('ICE connection state updated', { state: pc.iceConnectionState });
		});

		// Handle incoming tracks
		pc.addEventListener('track', (event) => {
			if (event.streams && event.streams[0]) {
				remoteStream = event.streams[0];
				logger.info('Received remote audio stream');
			}
		});

		// Add local stream if available
		if (localStream) {
			localStream.getTracks().forEach(track => {
				pc.addTrack(track, localStream!);
			});
		}

		return pc;
	}

	async function setupLocalAudio(): Promise<void> {
		if (!finalConfig.enableAudio) return;

		try {
			localStream = await navigator.mediaDevices.getUserMedia({
				audio: {
					sampleRate: 16000,
					channelCount: 1,
					echoCancellation: true,
					noiseSuppression: true,
					autoGainControl: true
				},
				video: false
			});

			// Setup audio level monitoring
			setupAudioLevelMonitoring();

			logger.info('Local audio stream established');
		} catch (error) {
			logger.error('Failed to setup local audio', error as Error);
			throw error;
		}
	}

	function setupAudioLevelMonitoring(): void {
		if (!localStream || !browser) return;

		// Create audio context for level monitoring
		audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
		analyser = audioContext.createAnalyser();
		analyser.fftSize = 256;
		analyser.smoothingTimeConstant = 0.8;

		const source = audioContext.createMediaStreamSource(localStream);
		source.connect(analyser);

		// Monitor audio levels
		audioLevelInterval = setInterval(() => {
			if (!analyser) return;

			const dataArray = new Uint8Array(analyser.frequencyBinCount);
			analyser.getByteFrequencyData(dataArray);

			// Calculate average level
			const average = dataArray.reduce((sum, value) => sum + value, 0) / dataArray.length;
			const normalizedLevel = average / 255;

			updateStats({ audioLevel: normalizedLevel });
		}, 100);
	}

	async function connectSignaling(url: string): Promise<void> {
		return new Promise((resolve, reject) => {
			signalingSocket = new WebSocket(url);

			signalingSocket.onopen = () => {
				logger.info('Signaling connected');
				resolve();
			};

			signalingSocket.onmessage = async (event) => {
				try {
					const message = JSON.parse(event.data);
					await handleSignalingMessage(message);
				} catch (error) {
					logger.error('Failed to handle signaling message', error as Error);
				}
			};

			signalingSocket.onerror = (error) => {
				logger.error('Signaling error', error as Error);
				reject(error);
			};

			signalingSocket.onclose = () => {
				logger.info('Signaling disconnected');
				if (finalConfig.autoReconnect && reconnectAttempts < finalConfig.maxReconnectAttempts) {
					scheduleReconnect();
				}
			};
		});
	}

	async function handleSignalingMessage(message: any): Promise<void> {
		if (!peerConnection) return;

		switch (message.type) {
			case 'offer':
				await handleOffer(message.offer);
				break;
			case 'answer':
				await handleAnswer(message.answer);
				break;
			case 'ice-candidate':
				await handleIceCandidate(message.candidate);
				break;
			default:
				logger.warn('Unknown signaling message type', { type: message.type });
		}
	}

	async function handleOffer(offer: RTCSessionDescriptionInit): Promise<void> {
		if (!peerConnection) return;

		await peerConnection.setRemoteDescription(offer);
		const answer = await peerConnection.createAnswer();
		await peerConnection.setLocalDescription(answer);

		sendSignalingMessage({
			type: 'answer',
			answer: answer
		});
	}

	async function handleAnswer(answer: RTCSessionDescriptionInit): Promise<void> {
		if (!peerConnection) return;
		await peerConnection.setRemoteDescription(answer);
	}

	async function handleIceCandidate(candidate: RTCIceCandidateInit): Promise<void> {
		if (!peerConnection) return;
		await peerConnection.addIceCandidate(candidate);
	}

	function sendSignalingMessage(message: any): void {
		if (signalingSocket && signalingSocket.readyState === WebSocket.OPEN) {
			signalingSocket.send(JSON.stringify(message));
		}
	}

	function scheduleReconnect(): void {
		if (reconnectTimeout) return;

		updateConnectionState('reconnecting');
		
		reconnectTimeout = setTimeout(async () => {
			reconnectTimeout = null;
			
			if (reconnectAttempts >= finalConfig.maxReconnectAttempts) {
				updateConnectionState('failed');
				return;
			}

			reconnectAttempts++;
			logger.info('WebRTC reconnection attempt', {
				attempt: reconnectAttempts,
				maxAttempts: finalConfig.maxReconnectAttempts
			});

			try {
				await disconnect();
				await connect(currentSignalingUrl);
			} catch (error) {
				logger.error('WebRTC reconnection failed', error as Error);
				scheduleReconnect();
			}
		}, finalConfig.reconnectInterval);
	}

	async function connect(signalingUrl: string): Promise<void> {
		if (!browser) {
			throw new Error('WebRTC not available outside browser');
		}

		currentSignalingUrl = signalingUrl;
		updateConnectionState('connecting');

		try {
			// Setup local audio
			await setupLocalAudio();

			// Initialize peer connection
			peerConnection = await initializePeerConnection();

			// Connect signaling
			await connectSignaling(signalingUrl);

			// Start stats monitoring
			startStatsMonitoring();

		} catch (error) {
			logger.error('Failed to connect WebRTC', error as Error);
			updateConnectionState('failed');
			throw error;
		}
	}

	async function disconnect(): Promise<void> {
		updateConnectionState('disconnected');

		// Clear reconnection timeout
		if (reconnectTimeout) {
			clearTimeout(reconnectTimeout);
			reconnectTimeout = null;
		}

		// Stop audio level monitoring
		if (audioLevelInterval) {
			clearInterval(audioLevelInterval);
			audioLevelInterval = null;
		}

		// Close audio context
		if (audioContext && audioContext.state !== 'closed') {
			await audioContext.close();
			audioContext = null;
		}

		// Stop local stream
		if (localStream) {
			localStream.getTracks().forEach(track => track.stop());
			localStream = null;
		}

		// Close peer connection
		if (peerConnection) {
			peerConnection.close();
			peerConnection = null;
		}

		// Close signaling socket
		if (signalingSocket) {
			signalingSocket.close();
			signalingSocket = null;
		}

		remoteStream = null;
		analyser = null;
	}

	function startStatsMonitoring(): void {
		if (!peerConnection) return;

		setInterval(async () => {
			if (!peerConnection || peerConnection.connectionState !== 'connected') return;

			try {
				const statsReport = await peerConnection.getStats();
				let totalLatency = 0;
				let packetsLost = 0;
				let packetsReceived = 0;
				let bitrate = 0;

				statsReport.forEach((report) => {
					if (report.type === 'remote-inbound-rtp' && report.kind === 'audio') {
						totalLatency = (report as any).roundTripTime || 0;
						packetsLost = (report as any).packetsLost || 0;
						packetsReceived = (report as any).packetsReceived || 0;
					}
					if (report.type === 'inbound-rtp' && report.kind === 'audio') {
						const bytesReceived = (report as any).bytesReceived || 0;
						const timestamp = (report as any).timestamp || 0;
						// Calculate approximate bitrate
						bitrate = (bytesReceived * 8) / 1000; // kbps
					}
				});

				const packetLossPercentage = packetsReceived > 0 ? (packetsLost / (packetsLost + packetsReceived)) * 100 : 0;

				updateStats({
					latency: totalLatency * 1000, // Convert to ms
					packetLoss: packetLossPercentage,
					bitrate
				});
			} catch (error) {
				logger.warn('Failed to get WebRTC stats', { error });
			}
		}, 1000);
	}

	async function switchProvider(newProvider: string): Promise<void> {
		const wasConnected = get(stats).connectionState === 'connected';
		const oldUrl = currentSignalingUrl;

		try {
			// Extract base URL and replace provider
			const baseUrl = oldUrl.split('/').slice(0, -1).join('/');
			const newUrl = `${baseUrl}/${newProvider}`;

			if (wasConnected) {
				await disconnect();
			}

			await connect(newUrl);
		} catch (error) {
			logger.error('Failed to switch provider', error as Error);
			
			// Try to reconnect to old provider
			if (wasConnected) {
				try {
					await connect(oldUrl);
				} catch (reconnectError) {
					logger.error('Failed to reconnect to previous provider', reconnectError as Error);
				}
			}
			
			throw error;
		}
	}

	function muteAudio(muted: boolean): void {
		if (localStream) {
			localStream.getAudioTracks().forEach(track => {
				track.enabled = !muted;
			});
		}
	}

	function sendAudioChunk(chunk: ArrayBuffer): void {
		// This would be implemented for custom audio streaming
		// For now, WebRTC handles audio streaming automatically
		logger.debug('Audio chunk received (WebRTC handles streaming automatically)');
	}

	async function startScreenShare(): Promise<MediaStream> {
		if (!browser) {
			throw new Error('Screen sharing not available outside browser');
		}

		try {
			screenStream = await navigator.mediaDevices.getDisplayMedia({
				video: {
					cursor: 'always',
					displaySurface: 'monitor'
				} as any,
				audio: false
			});

			screenTrack = screenStream.getVideoTracks()[0];

			// Handle user stopping share via browser UI
			screenTrack.onended = () => {
				stopScreenShare();
				logger.info('Screen share stopped by user');
			};

			// Add to peer connection if exists
			if (peerConnection) {
				peerConnection.addTrack(screenTrack, screenStream);
			}

			logger.info('Screen sharing started');
			return screenStream;
		} catch (error) {
			logger.error('Failed to start screen share', error as Error);
			throw new Error('Screen sharing denied or not supported');
		}
	}

	function stopScreenShare(): void {
		if (screenTrack) {
			screenTrack.stop();
			screenTrack = null;
		}

		if (screenStream) {
			screenStream.getTracks().forEach(track => track.stop());
			screenStream = null;
		}

		logger.info('Screen sharing stopped');
	}

	function getScreenShareStream(): MediaStream | null {
		return screenStream;
	}

	function isScreenSharing(): boolean {
		return screenStream !== null && screenTrack?.readyState === 'live';
	}

	async function cleanup(): Promise<void> {
		// Stop screen sharing if active
		stopScreenShare();

		await disconnect();
		await audioManager.cleanup();
	}

	return {
		subscribe: stats.subscribe,
		connect,
		disconnect,
		switchProvider,
		getConnectionState() {
			return get(stats).connectionState;
		},
		async getStats() {
			if (!peerConnection) return null;
			return await peerConnection.getStats();
		},
		muteAudio,
		sendAudioChunk,
		startScreenShare,
		stopScreenShare,
		getScreenShareStream,
		isScreenSharing,
		cleanup
	};
}
