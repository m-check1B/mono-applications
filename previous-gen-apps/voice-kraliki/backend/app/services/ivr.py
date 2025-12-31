"""IVR (Interactive Voice Response) Service.

Handles IVR flow execution, session management, and call navigation.
"""

import logging
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.ivr import IVRFlow, IVRFlowCreate, IVRFlowUpdate, IVRNodeType, IVRSession

logger = logging.getLogger(__name__)


class IVRExecutionError(Exception):
    """Base exception for IVR execution errors."""
    pass


class IVRService:
    """Service for managing IVR flows and sessions."""

    def __init__(self, db: Session):
        self.db = db

    # ===== Flow Management =====

    def create_flow(self, flow_data: IVRFlowCreate) -> IVRFlow:
        """Create a new IVR flow."""
        # Convert Pydantic model to dict for JSON serialization
        nodes_dict = {
            node_id: node_config.model_dump()
            for node_id, node_config in flow_data.nodes.items()
        }

        flow = IVRFlow(
            campaign_id=flow_data.campaign_id,
            team_id=flow_data.team_id,
            name=flow_data.name,
            description=flow_data.description,
            is_active=flow_data.is_active,
            entry_node_id=flow_data.entry_node_id,
            nodes=nodes_dict,
            default_language=flow_data.default_language,
            max_retries=flow_data.max_retries,
            timeout_seconds=flow_data.timeout_seconds,
            inter_digit_timeout=flow_data.inter_digit_timeout,
            invalid_input_message=flow_data.invalid_input_message,
            timeout_message=flow_data.timeout_message,
            error_node_id=flow_data.error_node_id
        )

        self.db.add(flow)
        self.db.commit()
        self.db.refresh(flow)

        logger.info(f"Created IVR flow: {flow.name} (ID: {flow.id})")
        return flow

    def get_flow(self, flow_id: int) -> IVRFlow | None:
        """Get an IVR flow by ID."""
        return self.db.query(IVRFlow).filter(IVRFlow.id == flow_id).first()

    def list_flows(
        self,
        campaign_id: int | None = None,
        team_id: int | None = None,
        is_active: bool | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[IVRFlow]:
        """List IVR flows with optional filters."""
        query = self.db.query(IVRFlow)

        if campaign_id is not None:
            query = query.filter(IVRFlow.campaign_id == campaign_id)
        if team_id is not None:
            query = query.filter(IVRFlow.team_id == team_id)
        if is_active is not None:
            query = query.filter(IVRFlow.is_active == is_active)

        return query.order_by(IVRFlow.created_at.desc()).offset(skip).limit(limit).all()

    def update_flow(self, flow_id: int, flow_data: IVRFlowUpdate) -> IVRFlow | None:
        """Update an IVR flow."""
        flow = self.get_flow(flow_id)
        if not flow:
            return None

        # Update fields
        update_data = flow_data.model_dump(exclude_unset=True)

        # Convert nodes to dict if provided
        if "nodes" in update_data and update_data["nodes"]:
            update_data["nodes"] = {
                node_id: node_config.model_dump()
                for node_id, node_config in update_data["nodes"].items()
            }

        for field, value in update_data.items():
            setattr(flow, field, value)

        flow.version += 1
        flow.updated_at = datetime.now(UTC)

        self.db.commit()
        self.db.refresh(flow)

        logger.info(f"Updated IVR flow: {flow.name} (ID: {flow.id}, version: {flow.version})")
        return flow

    def delete_flow(self, flow_id: int) -> bool:
        """Delete an IVR flow."""
        flow = self.get_flow(flow_id)
        if not flow:
            return False

        self.db.delete(flow)
        self.db.commit()

        logger.info(f"Deleted IVR flow: {flow.name} (ID: {flow.id})")
        return True

    def publish_flow(self, flow_id: int) -> IVRFlow | None:
        """Publish an IVR flow (mark as production-ready)."""
        flow = self.get_flow(flow_id)
        if not flow:
            return None

        flow.published_at = datetime.now(UTC)
        flow.is_active = True

        self.db.commit()
        self.db.refresh(flow)

        logger.info(f"Published IVR flow: {flow.name} (ID: {flow.id})")
        return flow

    # ===== Session Management =====

    def start_session(
        self,
        flow_id: int,
        call_sid: str,
        caller_phone: str | None = None,
        language: str | None = None
    ) -> tuple[IVRSession, dict[str, Any]]:
        """
        Start a new IVR session.

        Returns:
            Tuple of (session, initial_action) where initial_action describes what to play/do
        """
        flow = self.get_flow(flow_id)
        if not flow:
            raise IVRExecutionError(f"Flow {flow_id} not found")

        if not flow.is_active:
            raise IVRExecutionError(f"Flow {flow_id} is not active")

        # Create session
        session = IVRSession(
            flow_id=flow_id,
            call_sid=call_sid,
            caller_phone=caller_phone,
            language=language or flow.default_language,
            status="in_progress",
            current_node_id=flow.entry_node_id,
            started_at=datetime.now(UTC)
        )

        self.db.add(session)

        # Update flow stats
        flow.total_sessions += 1

        self.db.commit()
        self.db.refresh(session)

        logger.info(f"Started IVR session: {session.call_sid} for flow {flow.name}")

        # Get initial action
        initial_action = self._execute_node(session, flow, flow.entry_node_id)

        return session, initial_action

    def get_session(self, session_id: int) -> IVRSession | None:
        """Get an IVR session by ID."""
        return self.db.query(IVRSession).filter(IVRSession.id == session_id).first()

    def get_session_by_call_sid(self, call_sid: str) -> IVRSession | None:
        """Get an IVR session by call SID."""
        return self.db.query(IVRSession).filter(IVRSession.call_sid == call_sid).first()

    def handle_input(
        self,
        call_sid: str,
        user_input: str,
        input_type: str = "dtmf"
    ) -> dict[str, Any]:
        """
        Handle user input (DTMF or speech) and navigate to next node.

        Returns:
            Action to perform (play message, transfer, etc.)
        """
        session = self.get_session_by_call_sid(call_sid)
        if not session:
            raise IVRExecutionError(f"Session not found for call {call_sid}")

        flow = self.get_flow(session.flow_id)
        if not flow:
            raise IVRExecutionError(f"Flow {session.flow_id} not found")

        # Record input
        session.input_history.append({
            "node_id": session.current_node_id,
            "input": user_input,
            "type": input_type,
            "timestamp": datetime.now(UTC).isoformat()
        })

        # Get current node
        current_node = flow.nodes.get(session.current_node_id)
        if not current_node:
            raise IVRExecutionError(f"Node {session.current_node_id} not found")

        # Determine next node based on input
        next_node_id = self._get_next_node(current_node, user_input, session)

        if not next_node_id:
            # Invalid input - replay current node or go to error node
            retry_count = self._get_retry_count(session, session.current_node_id)

            if retry_count >= flow.max_retries:
                # Max retries exceeded - go to error node or end call
                if flow.error_node_id:
                    next_node_id = flow.error_node_id
                else:
                    return self._end_session(session, "max_retries_exceeded")
            else:
                # Replay current node with error message
                return {
                    "action": "invalid_input",
                    "message": flow.invalid_input_message or "Invalid input. Please try again.",
                    "retry_count": retry_count + 1,
                    "node_id": session.current_node_id,
                    "node": current_node
                }

        # Move to next node
        session.current_node_id = next_node_id
        session.node_history.append(next_node_id)

        self.db.commit()

        # Execute next node
        return self._execute_node(session, flow, next_node_id)

    def handle_timeout(self, call_sid: str) -> dict[str, Any]:
        """Handle input timeout."""
        session = self.get_session_by_call_sid(call_sid)
        if not session:
            raise IVRExecutionError(f"Session not found for call {call_sid}")

        flow = self.get_flow(session.flow_id)
        if not flow:
            raise IVRExecutionError(f"Flow {session.flow_id} not found")

        # Get current node
        current_node = flow.nodes.get(session.current_node_id)
        if not current_node:
            raise IVRExecutionError(f"Node {session.current_node_id} not found")

        # Check for timeout node
        if current_node.get("timeout_node"):
            next_node_id = current_node["timeout_node"]
            session.current_node_id = next_node_id
            session.node_history.append(next_node_id)
            self.db.commit()
            return self._execute_node(session, flow, next_node_id)

        # Check retry count
        retry_count = self._get_retry_count(session, session.current_node_id)

        if retry_count >= flow.max_retries:
            if flow.error_node_id:
                session.current_node_id = flow.error_node_id
                session.node_history.append(flow.error_node_id)
                self.db.commit()
                return self._execute_node(session, flow, flow.error_node_id)
            else:
                return self._end_session(session, "timeout")

        # Replay with timeout message
        return {
            "action": "timeout",
            "message": flow.timeout_message or "No input received. Please try again.",
            "retry_count": retry_count + 1,
            "node_id": session.current_node_id,
            "node": current_node
        }

    def end_session(
        self,
        call_sid: str,
        exit_reason: str,
        transferred_to: str | None = None
    ) -> IVRSession:
        """End an IVR session."""
        session = self.get_session_by_call_sid(call_sid)
        if not session:
            raise IVRExecutionError(f"Session not found for call {call_sid}")

        return self._end_session(session, exit_reason, transferred_to)

    # ===== Analytics =====

    def get_flow_analytics(
        self,
        flow_id: int,
        start_date: datetime | None = None,
        end_date: datetime | None = None
    ) -> dict[str, Any]:
        """Get analytics for an IVR flow."""
        flow = self.get_flow(flow_id)
        if not flow:
            return {}

        query = self.db.query(IVRSession).filter(IVRSession.flow_id == flow_id)

        if start_date:
            query = query.filter(IVRSession.started_at >= start_date)
        if end_date:
            query = query.filter(IVRSession.started_at <= end_date)

        sessions = query.all()

        total_sessions = len(sessions)
        completed = sum(1 for s in sessions if s.status == "completed")
        abandoned = sum(1 for s in sessions if s.status == "abandoned")
        in_progress = sum(1 for s in sessions if s.status == "in_progress")

        avg_duration = 0
        if sessions:
            durations = [s.duration_seconds for s in sessions if s.duration_seconds]
            avg_duration = sum(durations) / len(durations) if durations else 0

        # Node analytics
        node_stats = {}
        for session in sessions:
            for node_id in session.node_history:
                if node_id not in node_stats:
                    node_stats[node_id] = {"visits": 0, "sessions": set()}
                node_stats[node_id]["visits"] += 1
                node_stats[node_id]["sessions"].add(session.id)

        # Convert sets to counts
        for node_id in node_stats:
            node_stats[node_id]["unique_sessions"] = len(node_stats[node_id]["sessions"])
            del node_stats[node_id]["sessions"]

        return {
            "flow_id": flow_id,
            "flow_name": flow.name,
            "total_sessions": total_sessions,
            "completed_sessions": completed,
            "abandoned_sessions": abandoned,
            "in_progress_sessions": in_progress,
            "average_duration_seconds": avg_duration,
            "completion_rate": (completed / total_sessions * 100) if total_sessions > 0 else 0,
            "abandonment_rate": (abandoned / total_sessions * 100) if total_sessions > 0 else 0,
            "node_analytics": node_stats
        }

    # ===== Private Helper Methods =====

    def _execute_node(self, session: IVRSession, flow: IVRFlow, node_id: str) -> dict[str, Any]:
        """Execute a node and return the action to perform."""
        node = flow.nodes.get(node_id)
        if not node:
            raise IVRExecutionError(f"Node {node_id} not found in flow {flow.id}")

        node_type = node.get("type")

        # Add to history if not already there
        if not session.node_history or session.node_history[-1] != node_id:
            session.node_history.append(node_id)
            self.db.commit()

        # Handle different node types
        if node_type == IVRNodeType.MENU.value or node_type == IVRNodeType.GATHER_INPUT.value:
            return {
                "action": "gather_input",
                "node_id": node_id,
                "message": node.get("message"),
                "audio_url": node.get("audio_url"),
                "use_tts": node.get("use_tts", True),
                "input_type": node.get("input_type", "dtmf"),
                "num_digits": node.get("num_digits"),
                "finish_on_key": node.get("finish_on_key", "#"),
                "valid_inputs": node.get("valid_inputs") or list(node.get("options", {}).keys()),
                "timeout_seconds": flow.timeout_seconds
            }

        elif node_type == IVRNodeType.PLAY_MESSAGE.value:
            # Play message and auto-advance
            next_node = node.get("next_node")
            if next_node:
                session.current_node_id = next_node
                self.db.commit()
                # Return play action with auto-advance
                return {
                    "action": "play_and_continue",
                    "node_id": node_id,
                    "message": node.get("message"),
                    "audio_url": node.get("audio_url"),
                    "use_tts": node.get("use_tts", True),
                    "next_node": next_node
                }
            else:
                return self._end_session(session, "completed")

        elif node_type == IVRNodeType.TRANSFER.value:
            transfer_to = node.get("transfer_to")
            transfer_type = node.get("transfer_type", "queue")

            return self._end_session(session, "transferred", transfer_to)

        elif node_type == IVRNodeType.VOICEMAIL.value:
            return {
                "action": "voicemail",
                "node_id": node_id,
                "message": node.get("message", "Please leave a message after the tone.")
            }

        elif node_type == IVRNodeType.CONDITIONAL.value:
            # Evaluate condition
            condition = node.get("condition")
            result = self._evaluate_condition(condition, session)

            next_node = node.get("true_node") if result else node.get("false_node")

            if next_node:
                session.current_node_id = next_node
                self.db.commit()
                return self._execute_node(session, flow, next_node)
            else:
                return self._end_session(session, "completed")

        elif node_type == IVRNodeType.SET_VARIABLE.value:
            # Set session variable
            var_name = node.get("variable_name")
            var_value = node.get("variable_value")

            if var_name:
                session.variables[var_name] = var_value
                self.db.commit()

            next_node = node.get("next_node")
            if next_node:
                session.current_node_id = next_node
                self.db.commit()
                return self._execute_node(session, flow, next_node)
            else:
                return self._end_session(session, "completed")

        elif node_type == IVRNodeType.WEBHOOK.value:
            # For webhook, return action to caller to execute
            return {
                "action": "webhook",
                "node_id": node_id,
                "url": node.get("webhook_url"),
                "method": node.get("webhook_method", "POST"),
                "next_node": node.get("next_node")
            }

        elif node_type == IVRNodeType.END_CALL.value:
            return self._end_session(session, "completed")

        else:
            raise IVRExecutionError(f"Unknown node type: {node_type}")

    def _get_next_node(self, current_node: dict[str, Any], user_input: str, session: IVRSession) -> str | None:
        """Determine the next node based on user input."""
        node_type = current_node.get("type")

        if node_type == IVRNodeType.MENU.value:
            # Check menu options
            options = current_node.get("options", {})
            return options.get(user_input)

        elif node_type == IVRNodeType.GATHER_INPUT.value:
            # Store input as variable and move to next node
            var_name = current_node.get("variable_name", "user_input")
            session.variables[var_name] = user_input
            return current_node.get("next_node")

        return current_node.get("next_node")

    def _get_retry_count(self, session: IVRSession, node_id: str) -> int:
        """Get the number of times we've been at this node consecutively."""
        count = 0
        for i in range(len(session.node_history) - 1, -1, -1):
            if session.node_history[i] == node_id:
                count += 1
            else:
                break
        return count

    def _evaluate_condition(self, condition: str, session: IVRSession) -> bool:
        """Evaluate a conditional expression safely (no eval())."""
        if not condition:
            return True

        # Safe evaluation of simple conditions like "language == 'en'" or "count > 5"
        try:
            import operator
            import re

            # Supported operators (safe subset)
            ops = {
                '==': operator.eq,
                '!=': operator.ne,
                '>': operator.gt,
                '<': operator.lt,
                '>=': operator.ge,
                '<=': operator.le,
            }

            # Parse simple binary comparison: left op right
            pattern = r"^\s*(?P<left>[^<>=!]+?)\s*(?P<op>==|!=|>=|<=|>|<)\s*(?P<right>.+?)\s*$"
            match = re.match(pattern, condition)

            if not match:
                logger.warning(f"Complex condition not supported, returning False: {condition}")
                return False

            left_token = match.group("left").strip()
            right_token = match.group("right").strip()
            op_str = match.group("op")

            def _coerce_value(value: Any) -> Any:
                if isinstance(value, bool):
                    return value
                if isinstance(value, (int, float)):
                    return value
                if isinstance(value, str):
                    if re.fullmatch(r"-?\d+", value):
                        return int(value)
                    if re.fullmatch(r"-?\d+\.\d+", value):
                        return float(value)
                    return value
                return value

            def _resolve_operand(token: str) -> Any:
                if not token:
                    return ""
                if (token[0] == token[-1]) and token[0] in ("'", '"'):
                    return token[1:-1]
                if token in session.variables:
                    return _coerce_value(session.variables[token])
                lower = token.lower()
                if lower == "true":
                    return True
                if lower == "false":
                    return False
                return _coerce_value(token)

            left_val = _resolve_operand(left_token)
            right_val = _resolve_operand(right_token)

            if isinstance(left_val, bool) and isinstance(right_val, bool):
                return ops[op_str](left_val, right_val)

            left_is_num = isinstance(left_val, (int, float)) and not isinstance(left_val, bool)
            right_is_num = isinstance(right_val, (int, float)) and not isinstance(right_val, bool)
            if left_is_num and right_is_num:
                return ops[op_str](left_val, right_val)

            return ops[op_str](str(left_val), str(right_val))

        except Exception as e:
            logger.error(f"Error evaluating condition '{condition}': {e}")
            return False

    def _end_session(
        self,
        session: IVRSession,
        exit_reason: str,
        transferred_to: str | None = None
    ) -> dict[str, Any]:
        """End a session and update analytics."""
        session.status = "completed" if exit_reason == "completed" else "abandoned"
        session.ended_at = datetime.now(UTC)
        session.duration_seconds = int((session.ended_at - session.started_at).total_seconds())
        session.exit_reason = exit_reason
        session.exit_node_id = session.current_node_id

        if transferred_to:
            session.transferred_to = transferred_to

        # Update flow stats
        flow = self.get_flow(session.flow_id)
        if flow:
            if session.status == "completed":
                flow.completed_sessions += 1
            else:
                flow.abandoned_sessions += 1

            # Update average duration
            total_duration = flow.average_duration_seconds * (flow.total_sessions - 1) + session.duration_seconds
            flow.average_duration_seconds = total_duration / flow.total_sessions

        self.db.commit()

        logger.info(f"Ended IVR session: {session.call_sid}, reason: {exit_reason}")

        action_data = {
            "action": "end_call",
            "exit_reason": exit_reason,
            "session_id": session.id,
            "duration_seconds": session.duration_seconds
        }

        if transferred_to:
            action_data["action"] = "transfer"
            action_data["transfer_to"] = transferred_to

        return action_data
