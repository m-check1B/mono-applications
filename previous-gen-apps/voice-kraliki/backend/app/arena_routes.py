"""WebSocket handler for Voice Arena training sessions.

Provides WebRTC-based peer-to-peer audio communication between
trainees and AI personas for practice call scenarios.
"""

import asyncio
import logging
from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.services.voice_arena_service import (
    ArenaPersona,
    ArenaPersonaConfig,
    VoiceArenaService,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/arena", tags=["Voice Arena"])


class CreateSessionRequest(BaseModel):
    """Request to create a new arena session."""
    persona_type: str
    trainee_id: str | None = None


class CreateSessionResponse(BaseModel):
    """Response with new session details."""
    session_id: str
    persona_name: str
    arena_url: str


@router.post("/sessions", response_model=CreateSessionResponse)
async def create_arena_session(request: CreateSessionRequest) -> CreateSessionResponse:
    """Create a new Voice Arena training session.

    Args:
        request: Session creation request with persona type

    Returns:
        Session details including ID and arena URL
    """
    arena_service = VoiceArenaService()

    try:
        persona_enum = ArenaPersona(request.persona_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid persona type: {request.persona_type}. Available: {[p.value for p in ArenaPersona]}"
        )

    session = await arena_service.create_session(
        persona_type=persona_enum,
        trainee_id=request.trainee_id
    )

    return CreateSessionResponse(
        session_id=str(session.id),
        persona_name=session.persona_config.name,
        arena_url=f"/api/arena/{session.id}"
    )


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
) -> None:
    """
    WebSocket endpoint for Voice Arena peer-to-peer communication.

    Manages WebRTC signaling for direct audio communication
    between trainee and AI persona.

    Args:
        websocket: WebSocket connection
        session_id: Arena session identifier
    """
    try:
        # Accept WebSocket connection
        await websocket.accept()
        logger.info(f"Arena WebSocket connected for session {session_id}")

        # Initialize arena service
        arena_service = VoiceArenaService()
        session_uuid = UUID(session_id)

        # Verify session exists and get persona
        session = await arena_service.get_session(session_uuid)
        if not session:
            await websocket.send_json({
                "type": "error",
                "error": f"Session {session_id} not found"
            })
            return

        persona = session.persona_config
        logger.info(f"Arena session {session_id} using persona {persona.persona_type}")

        # Create WebRTC signaling handler
        webrtc_signaling = WebRTCSignalingHandler(websocket, session_uuid, persona)

        # Main message loop
        while True:
            message = await websocket.receive_json()
            message_type = message.get("type")

            if message_type == "webrtc-offer":
                # WebRTC offer from client
                await webrtc_signaling.handle_offer(message)

            elif message_type == "webrtc-answer":
                # WebRTC answer from client
                await webrtc_signaling.handle_answer(message)

            elif message_type == "webrtc-ice":
                # ICE candidate from client
                await webrtc_signaling.handle_ice(message)

            elif message_type == "webrtc-disconnect":
                # WebRTC disconnect
                await webrtc_signaling.handle_disconnect()

            elif message_type == "start-arena":
                # Start arena session
                await arena_service.start_session(session_uuid)
                await websocket.send_json({
                    "type": "arena-started",
                    "persona": persona.name,
                    "sessionState": "active"
                })

            elif message_type == "end-arena":
                # End arena session
                scorecard = message.get("scorecard")
                await arena_service.end_session(session_uuid, scorecard)
                await websocket.send_json({
                    "type": "arena-ended",
                    "duration": session.duration_seconds
                })

            elif message_type == "transcript":
                # Add transcript entry
                role = message.get("role", "trainee")
                content = message.get("content", "")
                await arena_service.add_transcript_entry(
                    session_uuid, role, content
                )

            elif message_type == "get-response":
                # Get AI persona response
                trainee_input = message.get("input", "")
                response = await arena_service.generate_persona_response(
                    session_uuid, trainee_input
                )
                await websocket.send_json({
                    "type": "persona-response",
                    "response": response,
                    "timestamp": asyncio.get_event_loop().time()
                })

            elif message_type == "ping":
                # Heartbeat
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": asyncio.get_event_loop().time()
                })

            else:
                logger.warning(f"Unknown message type: {message_type}")

    except WebSocketDisconnect:
        logger.info(f"Arena WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"Arena WebSocket error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "error": str(e)
            })
        except Exception:
            pass


class WebRTCSignalingHandler:
    """
    WebRTC signaling coordinator for peer-to-peer audio communication.

    Manages offer/answer/ICE exchange between trainee and AI persona.
    """

    def __init__(self, websocket: WebSocket, session_id: UUID, persona: ArenaPersonaConfig):
        self.websocket = websocket
        self.session_id = session_id
        self.persona = persona
        self.remote_description = None
        self.local_description = None

    async def handle_offer(self, message: dict[str, Any]) -> None:
        """
        Handle WebRTC offer from trainee (local side).

        Creates offer and sends to AI persona for answer.
        """
        offer_sdp = message.get("sdp")
        if not offer_sdp:
            logger.error("Missing SDP in offer")
            return

        self.local_description = {
            "type": "offer",
            "sdp": offer_sdp
        }

        await self.websocket.send_json({
            "type": "webrtc-answer",
            "sdp": await self._generate_answer_sdp(offer_sdp),
            "session_id": str(self.session_id)
        })

        logger.info(f"Sent WebRTC answer for session {self.session_id}")

    async def handle_answer(self, message: dict[str, Any]) -> None:
        """
        Handle WebRTC answer from AI persona.

        Sets remote description for peer connection.
        """
        answer_sdp = message.get("sdp")
        if not answer_sdp:
            logger.error("Missing SDP in answer")
            return

        self.remote_description = {
            "type": "answer",
            "sdp": answer_sdp
        }

        logger.info(f"Received WebRTC answer for session {self.session_id}")

    async def handle_ice(self, message: dict[str, Any]) -> None:
        """
        Handle ICE candidate exchange.

        """
        candidate = message.get("candidate")
        if not candidate:
            return

        await self.websocket.send_json({
            "type": "webrtc-candidate",
            "candidate": candidate,
            "session_id": str(self.session_id)
        })

        logger.debug(f"ICE candidate added for session {self.session_id}")

    async def handle_disconnect(self) -> None:
        """Handle WebRTC disconnection."""
        logger.info(f"WebRTC disconnected for session {self.session_id}")

    async def _generate_answer_sdp(self, offer_sdp: str) -> str:
        """
        Generate WebRTC answer SDP for AI persona.

        In production, this would use actual WebRTC API.
        For MVP, returns a basic answer.
        """
        # MVP: Just echo back with session context
        return "v=0\r\no=-\r\ns=-\r\nc=IN IP4 0.0.0.0.127.0.1\r\na=candidate:1 1 UDP 2130705436\r\na=candidate:2 1 UDP 2130705437\r\n"

    async def send_json(self, data: dict[str, Any]) -> None:
        """Send JSON message to WebSocket."""
        await self.websocket.send_json(data)


@router.get("/personas")
async def get_available_personas() -> dict[str, Any]:
    """
    Get list of available AI personas for arena.

    Returns:
        JSON response with persona configurations
    """
    arena_service = VoiceArenaService()
    personas = await arena_service.get_available_personas()

    return {
        "personas": [
            {
                "id": persona.persona_type,
                "name": persona.name,
                "description": persona.behavior_prompt,
                "emotional_state": persona.emotional_state,
                "response_style": persona.response_style
            }
            for persona in personas
        ]
    }


@router.get("/{session_id}", response_class=HTMLResponse)
async def get_arena_page(session_id: str) -> HTMLResponse:
    """
    Serve the Voice Arena page for a session.

    Args:
        session_id: Arena session identifier

    Returns:
        HTML response with arena interface
    """
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Voice Arena - AI Training</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            background: #1a1a2e;
            color: #ffffff;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }

        .header {
            background: #2d3748;
            padding: 1.5rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #374151;
        }

        .header h1 {
            color: #ffffff;
            font-size: 1.5rem;
            margin: 0;
        }

        .header .session-info {
            color: #ffffff80;
            font-size: 0.9rem;
        }

        .main {
            flex: 1;
            gap: 2rem;
            padding: 2rem;
            flex: 1;
        }

        .arena-controls {
            flex: 0 0 auto;
            width: 100%;
            max-width: 600px;
        }

        .control-group {
            background: #374151;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }

        .control-group h3 {
            color: #ffffff;
            font-size: 1rem;
            margin: 0 0 1rem;
        }

        .persona-select {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
        }

        .persona-card {
            background: #2d3748;
            border-radius: 8px;
            padding: 1rem;
            cursor: pointer;
            border: 2px solid transparent;
            transition: all 0.2s;
        }

        .persona-card:hover {
            border-color: #4f46e5;
            transform: translateY(-2px);
        }

        .persona-card.selected {
            border-color: #10b981;
            background: #1e40af;
        }

        .persona-name {
            color: #ffffff;
            font-weight: 600;
            margin-bottom: 0.25rem;
        }

        .persona-desc {
            color: #ffffff80;
            font-size: 0.85rem;
        }

        .session-status {
            background: #2d3748;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }

        .status-item {
            color: #ffffff;
            margin-bottom: 0.5rem;
        }

        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 0.5rem;
        }

        .status-indicator.active {
            background: #10b981;
            animation: pulse 2s infinite;
        }

        .status-indicator.inactive {
            background: #ffffff40;
        }

        .transcript {
            background: #374151;
            border-radius: 8px;
            padding: 1.5rem;
            min-height: 200px;
            max-height: 400px;
            overflow-y: auto;
        }

        .transcript-header {
            color: #ffffff;
            font-size: 0.9rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid #ffffff20;
        }

        .transcript-messages {
            space-y: 1rem;
        }

        .transcript-message {
            padding: 0.75rem;
            border-radius: 6px;
            margin-bottom: 0.5rem;
        }

        .transcript-message.trainee {
            background: #4a7c59;
            color: #ffffff;
        }

        .transcript-message.persona {
            background: #ef4444;
            color: #ffffff;
            margin-left: 1rem;
        }

        .transcript-message .role {
            font-weight: 600;
            margin-bottom: 0.25rem;
            font-size: 0.75rem;
            opacity: 0.7;
        }

        .transcript-message .content {
            font-size: 0.95rem;
        }

        .transcript-message .timestamp {
            font-size: 0.75rem;
            opacity: 0.5;
            margin-top: 0.25rem;
        }

        .action-buttons {
            display: flex;
            gap: 1rem;
            margin-top: 1.5rem;
        }

        .btn {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.95rem;
            font-weight: 600;
            transition: all 0.2s;
        }

        .btn-primary {
            background: #10b981;
            color: #ffffff;
        }

        .btn-primary:hover {
            background: #4f46e5;
        }

        .btn-danger {
            background: #ef4444;
            color: #ffffff;
        }

        .btn-danger:hover {
            background: #dc2626;
        }

        .btn-secondary {
            background: #ffffff20;
            color: #ffffff;
        }

        .btn-secondary:hover {
            background: #ffffff40;
        }

        .hidden {
            display: none;
        }

        @keyframes pulse {
            0%, 100% {
                opacity: 1;
            }
            50% {
                opacity: 0.5;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Voice Arena</h1>
        <div class="session-info">
            <span class="status-indicator inactive" id="status-dot"></span>
            <span id="status-text">Connecting...</span>
        </div>
    </div>

    <div class="main">
        <div class="arena-controls">
            <div class="control-group">
                <h3>1. Select AI Persona</h3>
                <div class="persona-select" id="persona-container">
                    <div class="persona-card" data-persona="angry_customer">
                        <div class="persona-name">Angry Customer</div>
                        <div class="persona-desc">Billing disputes, demanding immediate resolution</div>
                    </div>
                    <div class="persona-card" data-persona="curious_learner">
                        <div class="persona-name">Curious Learner</div>
                        <div class="persona-desc">New service, asking detailed questions</div>
                    </div>
                    <div class="persona-card" data-persona="confused_user">
                        <div class="persona-name">Confused User</div>
                        <div class="persona-desc">Technical issues, needs guidance</div>
                    </div>
                    <div class="persona-card" data-persona="satisfied_client">
                        <div class="persona-name">Satisfied Client</div>
                        <div class="persona-desc">Post-sale follow-up, positive</div>
                    </div>
                    <div class="persona-card" data-persona="persistent_issue_reporter">
                        <div class="persona-name">Persistent Issue Reporter</div>
                        <div class="persona-desc">Recurring problems, skeptical</div>
                    </div>
                </div>
            </div>

            <div class="control-group">
                <h3>2. Session Controls</h3>
                <div class="status-item">
                    <span class="status-indicator" id="session-status-dot"></span>
                    <span id="session-status-text">Not Started</span>
                </div>
                <div class="action-buttons">
                    <button class="btn btn-primary" id="start-btn" onclick="startArena()">Start Session</button>
                    <button class="btn btn-danger" id="end-btn" onclick="endArena()" disabled>End Session</button>
                </div>
            </div>
        </div>

        <div class="control-group">
            <h3>3. Transcript</h3>
            <div class="transcript">
                <div class="transcript-header">Conversation Log</div>
                <div class="transcript-messages" id="transcript-container">
                    <div class="transcript-message">
                        <em>Waiting for session to start...</em>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const sessionId = '${session_id}';
        const ws = new WebSocket(`ws://${window.location.host}/ws/arena/${sessionId}`);

        let currentPersona = null;
        let isSessionActive = false;

        ws.onopen = () => {
            console.log('Connected to arena WebSocket');
            updateStatus('connected', 'Session ready');
        };

        ws.onmessage = async (event) => {
            const data = JSON.parse(event.data);

            switch(data.type) {
                case 'persona-response':
                    addTranscriptMessage('persona', data.response);
                    break;

                case 'arena-started':
                    isSessionActive = true;
                    currentPersona = data.persona;
                    updateStatus('active', data.persona);
                    document.getElementById('start-btn').disabled = true;
                    document.getElementById('end-btn').disabled = false;
                    addSystemMessage(`Arena started with persona: ${data.persona}`);
                    break;

                case 'arena-ended':
                    isSessionActive = false;
                    const duration = data.duration || 0;
                    const minutes = Math.floor(duration / 60);
                    const seconds = duration % 60;
                    updateStatus('inactive', 'Session ended');
                    document.getElementById('start-btn').disabled = false;
                    document.getElementById('end-btn').disabled = true;
                    addSystemMessage(`Arena session ended. Duration: ${minutes}m ${seconds}s`);
                    break;

                case 'error':
                    addSystemMessage(`Error: ${data.error}`);
                    break;

                case 'pong':
                    break;

                default:
                    console.log('Unknown message type:', data.type);
            }
        };

        ws.onclose = () => {
            console.log('Disconnected from arena WebSocket');
            updateStatus('disconnected', 'Disconnected');
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            updateStatus('disconnected', 'Connection error');
        };

        function selectPersona(personaType) {
            ws.send(JSON.stringify({
                type: 'start-arena',
                persona: personaType
            }));
        }

        function startArena() {
            if (!currentPersona) {
                alert('Please select a persona first');
                return;
            }

            ws.send(JSON.stringify({
                type: 'start-arena',
                persona: currentPersona
            }));
        }

        function endArena() {
            if (!isSessionActive) {
                return;
            }

            ws.send(JSON.stringify({
                type: 'end-arena',
                scorecard: {
                    empathy: 5,
                    clarity: 4,
                    resolution: 5
                }
            }));
        }

        function sendTraineeInput() {
            const input = document.getElementById('trainee-input');
            if (input && input.value.trim()) {
                ws.send(JSON.stringify({
                    type: 'get-response',
                    input: input.value,
                    role: 'trainee'
                }));
                input.value = '';
            }
        }

        function addTranscriptMessage(role, content) {
            const container = document.getElementById('transcript-container');
            const msg = document.createElement('div');
            msg.className = `transcript-message ${role}`;
            msg.innerHTML = `
                <span class="role">${role.toUpperCase()}</span>
                <span class="content">${content}</span>
                <span class="timestamp">${new Date().toLocaleTimeString()}</span>
            `;
            container.appendChild(msg);
            container.scrollTop = container.scrollHeight;
        }

        function addSystemMessage(content) {
            const container = document.getElementById('transcript-container');
            const msg = document.createElement('div');
            msg.className = 'transcript-message';
            msg.innerHTML = `<em style="color: #ffffff80;">${content}</em>`;
            container.appendChild(msg);
            container.scrollTop = container.scrollHeight;
        }

        function updateStatus(state, text) {
            const statusDot = document.getElementById('status-dot');
            const statusText = document.getElementById('status-text');
            const sessionStatusDot = document.getElementById('session-status-dot');
            const sessionStatusText = document.getElementById('session-status-text');

            statusDot.className = `status-indicator ${state}`;
            statusText.textContent = text;

            if (state === 'connected') {
                sessionStatusDot.className = 'status-indicator inactive';
            } else if (state === 'active') {
                sessionStatusDot.className = 'status-indicator active';
            } else {
                sessionStatusDot.className = 'status-indicator inactive';
            }
        }

        // Initialize persona selection
        document.querySelectorAll('.persona-card').forEach(card => {
            card.addEventListener('click', () => {
                const personaType = card.getAttribute('data-persona');
                selectPersona(personaType);
                
                // Update selection UI
                document.querySelectorAll('.persona-card').forEach(c => c.classList.remove('selected'));
                card.classList.add('selected');
            });
        });
    </script>
</body>
</html>
    """

    return HTMLResponse(content=html_content)
