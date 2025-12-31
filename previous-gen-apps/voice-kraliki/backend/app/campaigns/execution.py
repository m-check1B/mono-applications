"""
Campaign script execution engine for managing call flow and state.
"""

import re
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .models import Campaign, ScriptStep, ScriptStepType, ValidationType


class ExecutionState(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    WAITING_FOR_RESPONSE = "waiting_for_response"
    PROCESSING_RESPONSE = "processing_response"
    TRANSFERRING = "transferring"
    COMPLETED = "completed"
    ERROR = "error"
    DISQUALIFIED = "disqualified"


@dataclass
class ExecutionContext:
    """Context for script execution containing state and collected data."""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    campaign_id: int = 0
    current_step: str = "start"
    step_index: int = 0
    state: ExecutionState = ExecutionState.IDLE
    collected_data: dict[str, Any] = field(default_factory=dict)
    execution_history: list[dict[str, Any]] = field(default_factory=list)
    current_response: Any | None = None
    error_message: str | None = None
    disposition: str | None = None


@dataclass
class ExecutionResult:
    """Result of a script execution step."""
    success: bool
    next_step: str | None = None
    message: str | None = None
    data_to_collect: dict[str, Any] | None = None
    disposition: str | None = None
    should_end_call: bool = False
    should_transfer: bool = False
    transfer_details: dict[str, Any] | None = None
    error: str | None = None


class FieldValidator:
    """Validates customer input based on field definitions."""

    @staticmethod
    def validate_field(value: Any, field_def: dict[str, Any]) -> tuple[bool, str | None]:
        """
        Validate a field value against its definition.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        validation_type = field_def.get("validation")

        if validation_type == ValidationType.STRING:
            if not isinstance(value, str) or not value.strip():
                return False, "Please provide a valid text response."

        elif validation_type == ValidationType.INTEGER:
            try:
                int_value = int(value)
                if int_value <= 0:
                    return False, "Please provide a positive number."
            except (ValueError, TypeError):
                return False, "Please provide a valid number."

        elif validation_type == ValidationType.BOOLEAN:
            if isinstance(value, str):
                value_lower = value.lower().strip()
                if value_lower not in ["yes", "no", "true", "false", "y", "n"]:
                    return False, "Please answer with yes or no."
                # Convert to boolean
                return True, None
            elif not isinstance(value, bool):
                return False, "Please answer with yes or no."

        elif validation_type == ValidationType.EMAIL:
            if isinstance(value, str):
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, value.strip()):
                    return False, "Please provide a valid email address."
            else:
                return False, "Please provide a valid email address."

        elif validation_type == ValidationType.PHONE:
            if isinstance(value, str):
                # Remove common formatting characters
                phone_clean = re.sub(r'[^\d]', '', value)
                if len(phone_clean) < 10:
                    return False, "Please provide a valid phone number."
            else:
                return False, "Please provide a valid phone number."

        return True, None

    @staticmethod
    def check_disqualification(value: Any, field_def: dict[str, Any]) -> str | None:
        """
        Check if a value should disqualify the lead.
        
        Returns:
            Disqualification reason or None if not disqualified
        """
        disqualification_rule = field_def.get("disqualificationRule")
        if not disqualification_rule:
            return None

        condition = disqualification_rule.get("condition")
        reason = disqualification_rule.get("reason")

        if not condition or not reason:
            return None

        # Simple condition evaluation (can be enhanced)
        try:
            # Handle numeric comparisons
            if ">" in condition:
                parts = condition.split(">")
                if len(parts) == 2:
                    field_name = parts[0].strip()
                    threshold = float(parts[1].strip())
                    if field_name == "value" and float(value) > threshold:
                        return reason

            elif "<" in condition:
                parts = condition.split("<")
                if len(parts) == 2:
                    field_name = parts[0].strip()
                    threshold = float(parts[1].strip())
                    if field_name == "value" and float(value) < threshold:
                        return reason

            elif ">=" in condition:
                parts = condition.split(">=")
                if len(parts) == 2:
                    field_name = parts[0].strip()
                    threshold = float(parts[1].strip())
                    if field_name == "value" and float(value) >= threshold:
                        return reason

            elif "<=" in condition:
                parts = condition.split("<=")
                if len(parts) == 2:
                    field_name = parts[0].strip()
                    threshold = float(parts[1].strip())
                    if field_name == "value" and float(value) <= threshold:
                        return reason

            elif "==" in condition:
                parts = condition.split("==")
                if len(parts) == 2:
                    field_name = parts[0].strip()
                    expected = parts[1].strip().strip('"\'')
                    if field_name == "value" and str(value) == expected:
                        return reason

        except (ValueError, TypeError, AttributeError):
            pass

        return None


class ScriptExecutor:
    """Executes campaign scripts with state management and conditional logic."""

    def __init__(self, campaign: Campaign):
        self.campaign = campaign
        self.validator = FieldValidator()

    def start_execution(self) -> ExecutionContext:
        """Start a new script execution."""
        context = ExecutionContext(
            campaign_id=self.campaign.id,
            current_step="start",
            state=ExecutionState.RUNNING
        )

        # Add to execution history
        context.execution_history.append({
            "action": "start",
            "step": "start",
            "timestamp": self._get_timestamp()
        })

        return context

    def execute_step(self, context: ExecutionContext) -> ExecutionResult:
        """
        Execute the current step in the script.
        
        Args:
            context: Current execution context
            
        Returns:
            ExecutionResult with next actions
        """
        try:
            # Get current script section
            script_section = getattr(self.campaign.script, context.current_step, None)
            if not script_section:
                # Try to get from script dict for dynamic sections
                script_section = self.campaign.script.get(context.current_step)

            if not script_section or context.step_index >= len(script_section):
                return ExecutionResult(
                    success=False,
                    error=f"Script section '{context.current_step}' not found or index out of bounds"
                )

            current_step = script_section[context.step_index]

            # Execute based on step type
            if current_step.type == ScriptStepType.STATEMENT:
                return self._execute_statement(current_step, context)

            elif current_step.type == ScriptStepType.QUESTION:
                return self._execute_question(current_step, context)

            elif current_step.type == ScriptStepType.CONDITIONAL:
                return self._execute_conditional(current_step, context)

            elif current_step.type == ScriptStepType.GO_TO:
                return self._execute_go_to(current_step, context)

            elif current_step.type == ScriptStepType.DISPOSITION:
                return self._execute_disposition(current_step, context)

            elif current_step.type == ScriptStepType.END_CALL:
                return self._execute_end_call(current_step, context)

            elif current_step.type == ScriptStepType.INITIATE_TRANSFER:
                return self._execute_initiate_transfer(current_step, context)

            else:
                return ExecutionResult(
                    success=False,
                    error=f"Unknown step type: {current_step.type}"
                )

        except Exception as e:
            return ExecutionResult(
                success=False,
                error=f"Script execution error: {str(e)}"
            )

    def process_response(self, context: ExecutionContext, response: Any) -> ExecutionResult:
        """
        Process a customer response and continue execution.
        
        Args:
            context: Current execution context
            response: Customer response
            
        Returns:
            ExecutionResult with next actions
        """
        context.current_response = response
        context.state = ExecutionState.PROCESSING_RESPONSE

        # Get current step to validate response
        script_section = getattr(self.campaign.script, context.current_step, None)
        if not script_section:
            script_section = self.campaign.script.get(context.current_step)

        if not script_section or context.step_index >= len(script_section):
            return ExecutionResult(
                success=False,
                error="No current step to validate response"
            )

        current_step = script_section[context.step_index]

        # Validate response if it's a question
        if current_step.type == ScriptStepType.QUESTION:
            validation_result = self._validate_response(current_step, response, context)
            if not validation_result.success:
                return validation_result

        # Store the response
        if current_step.response_variable:
            context.collected_data[current_step.response_variable] = response

        # Move to next step
        context.step_index += 1

        # Execute next step
        return self.execute_step(context)

    def _execute_statement(self, step: ScriptStep, context: ExecutionContext) -> ExecutionResult:
        """Execute a statement step."""
        content = self._resolve_content(step.content, step.content_from_field, context)

        # Add to execution history
        context.execution_history.append({
            "action": "statement",
            "content": content,
            "step": context.current_step,
            "index": context.step_index,
            "timestamp": self._get_timestamp()
        })

        # Move to next step
        context.step_index += 1

        return ExecutionResult(
            success=True,
            message=content,
            next_step=self._get_next_step_info(context)
        )

    def _execute_question(self, step: ScriptStep, context: ExecutionContext) -> ExecutionResult:
        """Execute a question step."""
        content = self._resolve_content(step.content, step.content_from_field, context)

        # Get field details for validation
        field_details = None
        if step.field_details:
            if isinstance(step.field_details, str):
                # Navigate to field definition
                field_details = self._get_field_definition(step.field_details)
            elif isinstance(step.field_details, list):
                # Multiple fields to gather
                field_details = [self._get_field_definition(field) for field in step.field_details]

        # Update state to wait for response
        context.state = ExecutionState.WAITING_FOR_RESPONSE

        return ExecutionResult(
            success=True,
            message=content,
            data_to_collect={
                "variable": step.response_variable,
                "field_details": field_details,
                "gather_fields": step.gather_fields
            }
        )

    def _execute_conditional(self, step: ScriptStep, context: ExecutionContext) -> ExecutionResult:
        """Execute a conditional step."""
        if not step.condition:
            return ExecutionResult(
                success=False,
                error="Conditional step missing condition"
            )

        # Evaluate condition
        condition_result = self._evaluate_condition(step.condition, context)

        if condition_result:
            # Condition is true, follow next_steps
            if step.next_steps:
                next_steps = step.next_steps
                if isinstance(next_steps, str):
                    next_steps = [next_steps]

                # Jump to first next step
                return self._jump_to_step(next_steps[0], context)
            else:
                # No next steps specified, move to next step
                context.step_index += 1
                return ExecutionResult(success=True)
        else:
            # Condition is false, move to next step
            context.step_index += 1
            return ExecutionResult(success=True)

    def _execute_go_to(self, step: ScriptStep, context: ExecutionContext) -> ExecutionResult:
        """Execute a go to step."""
        if not step.target:
            return ExecutionResult(
                success=False,
                error="Go to step missing target"
            )

        return self._jump_to_step(step.target, context)

    def _execute_disposition(self, step: ScriptStep, context: ExecutionContext) -> ExecutionResult:
        """Execute a disposition step."""
        disposition_value = step.value or "Completed"
        context.disposition = disposition_value
        context.state = ExecutionState.COMPLETED

        # Add to execution history
        context.execution_history.append({
            "action": "disposition",
            "value": disposition_value,
            "timestamp": self._get_timestamp()
        })

        return ExecutionResult(
            success=True,
            disposition=disposition_value,
            should_end_call=True
        )

    def _execute_end_call(self, step: ScriptStep, context: ExecutionContext) -> ExecutionResult:
        """Execute an end call step."""
        content = self._resolve_content(step.content, step.content_from_field, context)

        context.state = ExecutionState.COMPLETED

        # Add to execution history
        context.execution_history.append({
            "action": "end_call",
            "content": content,
            "timestamp": self._get_timestamp()
        })

        return ExecutionResult(
            success=True,
            message=content,
            should_end_call=True
        )

    def _execute_initiate_transfer(self, step: ScriptStep, context: ExecutionContext) -> ExecutionResult:
        """Execute a transfer step."""
        transfer_number = self._resolve_content(
            None, step.transfer_number, context
        ) if step.transfer_number else None

        context.state = ExecutionState.TRANSFERRING

        transfer_details = {
            "transfer_number": transfer_number,
            "on_agent_connect": step.on_agent_connect,
            "on_failure": step.on_failure
        }

        return ExecutionResult(
            success=True,
            should_transfer=True,
            transfer_details=transfer_details
        )

    def _validate_response(self, step: ScriptStep, response: Any, context: ExecutionContext) -> ExecutionResult:
        """Validate a customer response."""
        if not step.field_details:
            return ExecutionResult(success=True)

        field_def = self._get_field_definition(step.field_details)
        if not field_def:
            return ExecutionResult(success=True)

        # Validate the response
        is_valid, error_message = self.validator.validate_field(response, field_def)

        if not is_valid:
            # Check for invalid response handlers
            handlers = field_def.get("invalidResponseHandlers", [])
            for handler in handlers:
                if self._evaluate_condition(handler.get("condition", ""), context, response=response):
                    return ExecutionResult(
                        success=False,
                        message=handler.get("response", "Invalid response. Please try again."),
                        data_to_collect={
                            "variable": step.response_variable,
                            "field_details": field_def,
                            "retry": True
                        }
                    )

            return ExecutionResult(
                success=False,
                message=error_message or "Invalid response. Please try again.",
                data_to_collect={
                    "variable": step.response_variable,
                    "field_details": field_def,
                    "retry": True
                }
            )

        # Check for disqualification
        disqualification_reason = self.validator.check_disqualification(response, field_def)
        if disqualification_reason:
            context.disposition = disqualification_reason
            context.state = ExecutionState.DISQUALIFIED

            return ExecutionResult(
                success=True,
                disposition=disqualification_reason,
                should_end_call=True
            )

        return ExecutionResult(success=True)

    def _resolve_content(self, content: str | None, content_from_field: str | None,
                        context: ExecutionContext) -> str | None:
        """Resolve content from direct text or field reference."""
        if content:
            return content

        if content_from_field:
            # Navigate through the campaign structure to get the content
            parts = content_from_field.split('.')
            current = self.campaign

            for part in parts:
                if hasattr(current, part):
                    current = getattr(current, part)
                elif isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return content_from_field  # Return the field reference if not found

            return str(current) if current else content_from_field

        return None

    def _get_field_definition(self, field_path: str) -> dict[str, Any] | None:
        """Get field definition from the campaign structure."""
        parts = field_path.split('.')
        current = self.campaign

        for part in parts:
            if hasattr(current, part):
                current = getattr(current, part)
            elif isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

        if isinstance(current, dict):
            return current

        return None

    def _evaluate_condition(self, condition: str, context: ExecutionContext, response: Any = None) -> bool:
        """Evaluate a conditional expression."""
        if not condition:
            return False

        # Replace variables with actual values
        eval_condition = condition

        # Replace response variable if evaluating response
        if response is not None and "response" in eval_condition:
            eval_condition = eval_condition.replace("response", str(response))

        # Replace collected data variables
        for var_name, var_value in context.collected_data.items():
            if f"response.{var_name}" in eval_condition:
                eval_condition = eval_condition.replace(f"response.{var_name}", str(var_value))
            elif var_name in eval_condition:
                eval_condition = eval_condition.replace(var_name, str(var_value))

        # Simple boolean evaluations (can be enhanced with proper expression parsing)
        try:
            # Handle common boolean patterns
            if "==" in eval_condition:
                left, right = eval_condition.split("==", 1)
                left_val = self._evaluate_expression(left.strip(), context, response)
                right_val = self._evaluate_expression(right.strip(), context, response)
                return left_val == right_val

            elif "!=" in eval_condition:
                left, right = eval_condition.split("!=", 1)
                left_val = self._evaluate_expression(left.strip(), context, response)
                right_val = self._evaluate_expression(right.strip(), context, response)
                return left_val != right_val

            elif ">" in eval_condition:
                left, right = eval_condition.split(">", 1)
                left_val = float(self._evaluate_expression(left.strip(), context, response))
                right_val = float(self._evaluate_expression(right.strip(), context, response))
                return left_val > right_val

            elif "<" in eval_condition:
                left, right = eval_condition.split("<", 1)
                left_val = float(self._evaluate_expression(left.strip(), context, response))
                right_val = float(self._evaluate_expression(right.strip(), context, response))
                return left_val < right_val

            elif ">=" in eval_condition:
                left, right = eval_condition.split(">=", 1)
                left_val = float(self._evaluate_expression(left.strip(), context, response))
                right_val = float(self._evaluate_expression(right.strip(), context, response))
                return left_val >= right_val

            elif "<=" in eval_condition:
                left, right = eval_condition.split("<=", 1)
                left_val = float(self._evaluate_expression(left.strip(), context, response))
                right_val = float(self._evaluate_expression(right.strip(), context, response))
                return left_val <= right_val

            else:
                # Direct boolean evaluation
                return bool(self._evaluate_expression(eval_condition.strip(), context, response))

        except (ValueError, TypeError, AttributeError):
            return False

    def _evaluate_expression(self, expr: str, context: ExecutionContext, response: Any = None) -> Any:
        """Evaluate a single expression."""
        expr = expr.strip().strip('"\'')

        # Check if it's a response variable
        if expr.startswith("response."):
            var_name = expr[9:]  # Remove "response."
            if response is not None and var_name == "value":
                return response
            return context.collected_data.get(var_name)

        # Check if it's a collected data variable
        if expr in context.collected_data:
            return context.collected_data[expr]

        # Check if it's a boolean literal
        if expr.lower() in ["true", "yes", "y"]:
            return True
        elif expr.lower() in ["false", "no", "n"]:
            return False

        # Try to parse as number
        try:
            if '.' in expr:
                return float(expr)
            else:
                return int(expr)
        except ValueError:
            pass

        # Return as string
        return expr

    def _jump_to_step(self, target_step: str, context: ExecutionContext) -> ExecutionResult:
        """Jump to a specific step in the script."""
        context.current_step = target_step
        context.step_index = 0

        # Add to execution history
        context.execution_history.append({
            "action": "jump_to",
            "target": target_step,
            "timestamp": self._get_timestamp()
        })

        return ExecutionResult(
            success=True,
            next_step=target_step
        )

    def _get_next_step_info(self, context: ExecutionContext) -> str | None:
        """Get information about the next step."""
        script_section = getattr(self.campaign.script, context.current_step, None)
        if not script_section:
            script_section = self.campaign.script.get(context.current_step)

        if script_section and context.step_index < len(script_section):
            next_step = script_section[context.step_index]
            return f"{context.current_step}[{context.step_index}]: {next_step.type.value}"

        return None

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
