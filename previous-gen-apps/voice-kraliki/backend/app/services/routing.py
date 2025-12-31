"""Call Routing Service.

Implements intelligent call routing based on rules, conditions, and strategies.
"""

import logging
import re
from datetime import UTC, datetime
from typing import Any

import pytz
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.routing import (
    CallRoutingStrategy,
    ConditionOperator,
    RouteCallRequest,
    RoutingLog,
    RoutingRule,
    RoutingRuleCreate,
    RoutingRuleUpdate,
    RoutingTarget,
    RoutingTargetCreate,
    TargetType,
)
from app.models.supervisor import ActiveCall
from app.models.team import AgentProfile, AgentStatus

logger = logging.getLogger(__name__)


class RoutingError(Exception):
    """Base exception for routing errors."""
    pass


class RoutingService:
    """Service for managing call routing."""

    def __init__(self, db: Session):
        self.db = db

    # ===== Rule Management =====

    def create_rule(self, rule_data: RoutingRuleCreate) -> RoutingRule:
        """Create a new routing rule."""
        # Convert conditions to dict for JSON serialization
        conditions_dict = [cond.model_dump() for cond in rule_data.conditions]

        rule = RoutingRule(
            campaign_id=rule_data.campaign_id,
            team_id=rule_data.team_id,
            name=rule_data.name,
            description=rule_data.description,
            is_active=rule_data.is_active,
            priority=rule_data.priority,
            strategy=rule_data.strategy.value,
            conditions=conditions_dict,
            business_hours_only=rule_data.business_hours_only,
            active_hours=rule_data.active_hours,
            timezone=rule_data.timezone,
            fallback_enabled=rule_data.fallback_enabled,
            fallback_rule_id=rule_data.fallback_rule_id,
            fallback_action=rule_data.fallback_action,
            max_wait_time_seconds=rule_data.max_wait_time_seconds,
            enable_load_balancing=rule_data.enable_load_balancing,
            load_balance_threshold=rule_data.load_balance_threshold
        )

        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)

        logger.info(f"Created routing rule: {rule.name} (ID: {rule.id})")
        return rule

    def get_rule(self, rule_id: int) -> RoutingRule | None:
        """Get a routing rule by ID."""
        return self.db.query(RoutingRule).filter(RoutingRule.id == rule_id).first()

    def list_rules(
        self,
        campaign_id: int | None = None,
        team_id: int | None = None,
        is_active: bool | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[RoutingRule]:
        """List routing rules with optional filters."""
        query = self.db.query(RoutingRule)

        if campaign_id is not None:
            query = query.filter(RoutingRule.campaign_id == campaign_id)
        if team_id is not None:
            query = query.filter(RoutingRule.team_id == team_id)
        if is_active is not None:
            query = query.filter(RoutingRule.is_active == is_active)

        return query.order_by(RoutingRule.priority.asc(), RoutingRule.created_at.desc()).offset(skip).limit(limit).all()

    def update_rule(self, rule_id: int, rule_data: RoutingRuleUpdate) -> RoutingRule | None:
        """Update a routing rule."""
        rule = self.get_rule(rule_id)
        if not rule:
            return None

        update_data = rule_data.model_dump(exclude_unset=True)

        # Convert conditions if provided
        if "conditions" in update_data and update_data["conditions"]:
            update_data["conditions"] = [cond.model_dump() for cond in update_data["conditions"]]

        # Convert strategy enum if provided
        if "strategy" in update_data and update_data["strategy"]:
            update_data["strategy"] = update_data["strategy"].value

        for field, value in update_data.items():
            setattr(rule, field, value)

        rule.updated_at = datetime.now(UTC)

        self.db.commit()
        self.db.refresh(rule)

        logger.info(f"Updated routing rule: {rule.name} (ID: {rule.id})")
        return rule

    def delete_rule(self, rule_id: int) -> bool:
        """Delete a routing rule."""
        rule = self.get_rule(rule_id)
        if not rule:
            return False

        self.db.delete(rule)
        self.db.commit()

        logger.info(f"Deleted routing rule: {rule.name} (ID: {rule.id})")
        return True

    # ===== Target Management =====

    def add_target(self, target_data: RoutingTargetCreate) -> RoutingTarget:
        """Add a target to a routing rule."""
        target = RoutingTarget(
            rule_id=target_data.rule_id,
            target_type=target_data.target_type.value,
            target_id=target_data.target_id,
            target_name=target_data.target_name,
            weight=target_data.weight,
            is_active=target_data.is_active,
            required_skills=target_data.required_skills,
            min_skill_level=target_data.min_skill_level,
            required_languages=target_data.required_languages,
            priority=target_data.priority
        )

        self.db.add(target)
        self.db.commit()
        self.db.refresh(target)

        logger.info(f"Added target {target_data.target_id} to rule {target_data.rule_id}")
        return target

    def get_rule_targets(self, rule_id: int) -> list[RoutingTarget]:
        """Get all targets for a routing rule."""
        return self.db.query(RoutingTarget).filter(
            RoutingTarget.rule_id == rule_id,
            RoutingTarget.is_active == True
        ).order_by(RoutingTarget.priority.asc()).all()

    def remove_target(self, target_id: int) -> bool:
        """Remove a target from a routing rule."""
        target = self.db.query(RoutingTarget).filter(RoutingTarget.id == target_id).first()
        if not target:
            return False

        self.db.delete(target)
        self.db.commit()
        return True

    # ===== Call Routing Logic =====

    def route_call(self, request: RouteCallRequest) -> dict[str, Any]:
        """
        Route a call based on routing rules.

        Returns:
            Dict with routing decision
        """
        start_time = datetime.now(UTC)

        try:
            # Get applicable rules sorted by priority
            rules = self._get_applicable_rules(request)

            if not rules:
                return self._create_routing_result(
                    request=request,
                    success=False,
                    start_time=start_time,
                    message="No applicable routing rules found"
                )

            # Try each rule in priority order
            for rule in rules:
                # Check if rule conditions match
                if not self._evaluate_conditions(rule, request):
                    continue

                # Check business hours if required
                if rule.business_hours_only and not self._is_within_business_hours(rule):
                    continue

                # Get targets for this rule
                targets = self.get_rule_targets(rule.id)
                if not targets:
                    continue

                # Select target based on strategy
                target = self._select_target(rule, targets, request)

                if target:
                    # Log successful routing
                    return self._create_routing_result(
                        request=request,
                        success=True,
                        start_time=start_time,
                        rule=rule,
                        target=target,
                        message="Call routed successfully"
                    )

            # No rule matched - try fallback
            return self._handle_fallback(request, start_time)

        except Exception as e:
            logger.error(f"Error routing call {request.call_sid}: {e}")
            return self._create_routing_result(
                request=request,
                success=False,
                start_time=start_time,
                message=f"Routing error: {str(e)}"
            )

    def _get_applicable_rules(self, request: RouteCallRequest) -> list[RoutingRule]:
        """Get rules applicable to this call."""
        query = self.db.query(RoutingRule).filter(
            RoutingRule.is_active == True
        )

        if request.campaign_id:
            query = query.filter(
                or_(
                    RoutingRule.campaign_id == request.campaign_id,
                    RoutingRule.campaign_id == None
                )
            )

        return query.order_by(RoutingRule.priority.asc()).all()

    def _evaluate_conditions(self, rule: RoutingRule, request: RouteCallRequest) -> bool:
        """Evaluate if call matches rule conditions."""
        if not rule.conditions:
            return True  # No conditions = always match

        # Build context for evaluation
        context = {
            "caller_phone": request.caller_phone,
            "caller_priority": request.caller_priority or 0,
            "campaign_id": request.campaign_id,
            "required_skills": request.required_skills,
            "preferred_language": request.preferred_language,
            "time_of_day": datetime.now(UTC).strftime("%H:%M"),
            "day_of_week": datetime.now(UTC).strftime("%A").lower(),
            **request.metadata
        }

        result = True
        current_logic = "AND"

        for condition in rule.conditions:
            field = condition.get("field")
            operator = condition.get("operator")
            value = condition.get("value")
            logic = condition.get("logic", "AND")

            # Get field value from context
            field_value = context.get(field)

            # Evaluate condition
            condition_result = self._evaluate_condition(field_value, operator, value)

            # Apply logic
            if current_logic == "AND":
                result = result and condition_result
            else:  # OR
                result = result or condition_result

            current_logic = logic

        return result

    def _evaluate_condition(self, field_value: Any, operator: str, expected_value: Any) -> bool:
        """Evaluate a single condition."""
        try:
            if operator == ConditionOperator.EQUALS.value:
                return field_value == expected_value

            elif operator == ConditionOperator.NOT_EQUALS.value:
                return field_value != expected_value

            elif operator == ConditionOperator.CONTAINS.value:
                return expected_value in str(field_value) if field_value else False

            elif operator == ConditionOperator.STARTS_WITH.value:
                return str(field_value).startswith(str(expected_value)) if field_value else False

            elif operator == ConditionOperator.ENDS_WITH.value:
                return str(field_value).endswith(str(expected_value)) if field_value else False

            elif operator == ConditionOperator.GREATER_THAN.value:
                return float(field_value) > float(expected_value) if field_value else False

            elif operator == ConditionOperator.LESS_THAN.value:
                return float(field_value) < float(expected_value) if field_value else False

            elif operator == ConditionOperator.IN_LIST.value:
                return field_value in expected_value if isinstance(expected_value, list) else False

            elif operator == ConditionOperator.NOT_IN_LIST.value:
                return field_value not in expected_value if isinstance(expected_value, list) else True

            elif operator == ConditionOperator.MATCHES_REGEX.value:
                return bool(re.match(expected_value, str(field_value))) if field_value else False

            else:
                logger.warning(f"Unknown operator: {operator}")
                return False

        except Exception as e:
            logger.error(f"Error evaluating condition: {e}")
            return False

    def _is_within_business_hours(self, rule: RoutingRule) -> bool:
        """Check if current time is within business hours."""
        if not rule.active_hours:
            return True

        try:
            tz = pytz.timezone(rule.timezone)
            now = datetime.now(tz)
            current_day = now.strftime("%A").lower()
            current_time = now.time()

            hours = rule.active_hours.get(current_day)
            if not hours or len(hours) != 2:
                return False

            start_time = datetime.strptime(hours[0], "%H:%M").time()
            end_time = datetime.strptime(hours[1], "%H:%M").time()

            return start_time <= current_time <= end_time

        except Exception as e:
            logger.error(f"Error checking business hours: {e}")
            return False

    def _select_target(
        self,
        rule: RoutingRule,
        targets: list[RoutingTarget],
        request: RouteCallRequest
    ) -> RoutingTarget | None:
        """Select the best target based on routing strategy."""
        strategy = rule.strategy

        if strategy == CallRoutingStrategy.SKILL_BASED.value:
            return self._select_by_skills(targets, request.required_skills)

        elif strategy == CallRoutingStrategy.LEAST_BUSY.value:
            return self._select_least_busy(targets)

        elif strategy == CallRoutingStrategy.LONGEST_IDLE.value:
            return self._select_longest_idle(targets)

        elif strategy == CallRoutingStrategy.ROUND_ROBIN.value:
            return self._select_round_robin(targets, rule)

        elif strategy == CallRoutingStrategy.LANGUAGE.value:
            return self._select_by_language(targets, request.preferred_language)

        elif strategy == CallRoutingStrategy.PRIORITY.value:
            return targets[0] if targets else None  # Already sorted by priority

        else:
            # Default: first active target
            return targets[0] if targets else None

    def _select_by_skills(self, targets: list[RoutingTarget], required_skills: list[str]) -> RoutingTarget | None:
        """Select target with best skill match."""
        if not required_skills:
            return targets[0] if targets else None

        best_target = None
        best_score = -1

        for target in targets:
            if target.target_type != TargetType.AGENT.value:
                continue

            # Get agent profile
            agent = self.db.query(AgentProfile).filter(
                AgentProfile.id == int(target.target_id),
                AgentProfile.status == AgentStatus.AVAILABLE.value
            ).first()

            if not agent or not agent.skills:
                continue

            # Calculate skill match score
            agent_skills = agent.skills if isinstance(agent.skills, list) else []
            matched_skills = set(required_skills) & set(agent_skills)
            score = len(matched_skills) / len(required_skills) if required_skills else 0

            if score > best_score and score >= (target.min_skill_level / 10.0):
                best_score = score
                best_target = target

        return best_target

    def _select_least_busy(self, targets: list[RoutingTarget]) -> RoutingTarget | None:
        """Select target with fewest active calls."""
        for target in targets:
            if target.target_type != TargetType.AGENT.value:
                continue

            # Check if agent is available and not overloaded
            active_calls = self.db.query(ActiveCall).filter(
                ActiveCall.agent_id == int(target.target_id),
                ActiveCall.status.in_(["ringing", "connected"])
            ).count()

            if active_calls < 3:  # Max 3 calls per agent
                return target

        return None

    def _select_longest_idle(self, targets: list[RoutingTarget]) -> RoutingTarget | None:
        """Select agent who has been idle the longest."""
        best_target = None
        longest_idle = None

        for target in targets:
            if target.target_type != TargetType.AGENT.value:
                continue

            agent = self.db.query(AgentProfile).filter(
                AgentProfile.id == int(target.target_id),
                AgentProfile.status == AgentStatus.AVAILABLE.value
            ).first()

            if agent and agent.last_active_at:
                if longest_idle is None or agent.last_active_at < longest_idle:
                    longest_idle = agent.last_active_at
                    best_target = target

        return best_target or (targets[0] if targets else None)

    def _select_round_robin(self, targets: list[RoutingTarget], rule: RoutingRule) -> RoutingTarget | None:
        """Select next target in round-robin fashion."""
        # Simple round-robin based on total calls routed
        index = rule.total_calls_routed % len(targets) if targets else 0
        return targets[index] if 0 <= index < len(targets) else None

    def _select_by_language(self, targets: list[RoutingTarget], language: str | None) -> RoutingTarget | None:
        """Select target that speaks the required language."""
        if not language:
            return targets[0] if targets else None

        for target in targets:
            if language in target.required_languages:
                return target

        return targets[0] if targets else None

    def _handle_fallback(self, request: RouteCallRequest, start_time: datetime) -> dict[str, Any]:
        """Handle fallback when no rule matches."""
        # Default fallback: voicemail or queue
        return self._create_routing_result(
            request=request,
            success=True,
            start_time=start_time,
            fallback_used=True,
            fallback_target="voicemail",
            message="No rules matched - routed to voicemail"
        )

    def _create_routing_result(
        self,
        request: RouteCallRequest,
        success: bool,
        start_time: datetime,
        rule: RoutingRule | None = None,
        target: RoutingTarget | None = None,
        fallback_used: bool = False,
        fallback_target: str | None = None,
        message: str | None = None
    ) -> dict[str, Any]:
        """Create routing result and log to database."""
        end_time = datetime.now(UTC)
        duration_ms = int((end_time - start_time).total_seconds() * 1000)

        # Create log entry
        log = RoutingLog(
            rule_id=rule.id if rule else None,
            call_sid=request.call_sid,
            caller_phone=request.caller_phone,
            caller_priority=request.caller_priority,
            campaign_id=request.campaign_id,
            matched_rule_name=rule.name if rule else None,
            strategy_used=rule.strategy if rule else None,
            target_type=target.target_type if target else None,
            target_id=target.target_id if target else None,
            target_name=target.target_name if target else None,
            route_start_time=start_time,
            route_end_time=end_time,
            route_duration_ms=duration_ms,
            success=success,
            failure_reason=message if not success else None,
            fallback_used=fallback_used,
            fallback_target=fallback_target
        )

        self.db.add(log)

        # Update rule stats if successful
        if rule and success:
            rule.total_calls_routed += 1
            rule.successful_routes += 1
            rule.last_used_at = datetime.now(UTC)

            # Update average route time
            total_time = rule.average_route_time_ms * (rule.total_calls_routed - 1) + duration_ms
            rule.average_route_time_ms = total_time / rule.total_calls_routed

        self.db.commit()

        return {
            "success": success,
            "rule_used": rule.name if rule else None,
            "strategy": rule.strategy if rule else None,
            "target_type": target.target_type if target else fallback_target,
            "target_id": target.target_id if target else None,
            "target_name": target.target_name if target else None,
            "route_time_ms": duration_ms,
            "fallback_used": fallback_used,
            "message": message
        }

    # ===== Analytics =====

    def get_routing_analytics(
        self,
        rule_id: int | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None
    ) -> dict[str, Any]:
        """Get routing analytics."""
        query = self.db.query(RoutingLog)

        if rule_id:
            query = query.filter(RoutingLog.rule_id == rule_id)
        if start_date:
            query = query.filter(RoutingLog.route_start_time >= start_date)
        if end_date:
            query = query.filter(RoutingLog.route_start_time <= end_date)

        logs = query.all()

        total = len(logs)
        successful = sum(1 for log in logs if log.success)
        failed = total - successful
        fallback_count = sum(1 for log in logs if log.fallback_used)

        avg_duration = 0
        if logs:
            durations = [log.route_duration_ms for log in logs if log.route_duration_ms]
            avg_duration = sum(durations) / len(durations) if durations else 0

        return {
            "total_calls": total,
            "successful_routes": successful,
            "failed_routes": failed,
            "success_rate": (successful / total * 100) if total > 0 else 0,
            "fallback_count": fallback_count,
            "average_route_time_ms": avg_duration
        }
