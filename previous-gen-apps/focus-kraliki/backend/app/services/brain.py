"""
Focus Brain - The Central AI Intelligence

Focus by Kraliki is an AI-FIRST capture and productivity system.
NOT just a task list - it captures ideas, notes, goals, plans, strategies.

The Brain helps humans:
1. Capture anything - speak or type, AI categorizes automatically
2. Understand and break down goals into actionable items
3. Organize knowledge by custom types (Ideas, Notes, Plans, Goals, etc.)
4. Prioritize and suggest what to work on next
5. Optionally integrate with Kraliki AI swarm for automation

AI-First Capture:
- User says "I have an idea for..." → Brain creates Idea
- User says "My goal is..." → Brain creates Goal/Plan
- User says "Note to self..." → Brain creates Note
- User says anything → Brain auto-categorizes to right type

Architecture:
- Focus = Ground level, where humans capture and organize
- Knowledge Layer = Multi-type system (Ideas, Notes, Tasks, Plans, custom types)
- Kraliki = Above, AI swarm that can execute tasks from Focus
- Focus works standalone; Kraliki integration is optional

Policy: No hardcoding of models or prompts.
- Models come from config.py (BRAIN_MODEL, BRAIN_MODEL_PROVIDER)
- Prompts come from config/brain_prompts.json
- Use ai_providers.py for all AI calls
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.ai_providers import get_ai_provider, get_prompt
from app.core.security import generate_id
from app.models.task import Task, TaskStatus, Project
from app.models.knowledge_item import KnowledgeItem
from app.models.item_type import ItemType
from app.models.user import User
from app.services.ai_scheduler import AISchedulerService
from app.services.flow_memory import FlowMemoryService
from app.services.shadow_analyzer import ShadowAnalyzerService
from app.services.knowledge_defaults import ensure_default_item_types


class FocusBrain:
    """
    The Brain orchestrates all Focus intelligence.

    Usage:
        brain = FocusBrain(user_id, db)

        # Parse a goal
        result = await brain.understand_goal("Launch my SaaS by March")

        # Get daily plan
        plan = await brain.get_daily_plan()

        # Ask anything
        response = await brain.ask("What should I work on?")
    """

    def __init__(self, user: User, db: Session):
        self.user = user
        self.user_id = str(user.id)
        self.db = db
        self.scheduler = AISchedulerService()
        self.memory = FlowMemoryService()

    async def understand_goal(self, goal_text: str) -> Dict[str, Any]:
        """
        Parse natural language goal into structured format.

        Example:
            Input: "Launch my product by February 2026"
            Output: {
                "goal": "Launch product",
                "deadline": "2026-02-28",
                "suggested_project": "Product Launch",
                "suggested_tasks": [
                    "Define MVP features",
                    "Build landing page",
                    "Set up payments",
                    "Beta testing",
                    "Launch marketing",
                    "Go live"
                ]
            }
        """
        # Get prompt from external file (no hardcoding)
        prompt = get_prompt("understand_goal", "parse", goal=goal_text)

        try:
            # Use configured AI provider (no hardcoded models)
            provider = get_ai_provider()
            response_text = await provider.generate(prompt, max_tokens=1024)

            # Try to find JSON in response
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0]
            else:
                json_str = response_text

            parsed = json.loads(json_str.strip())

            # Store in memory
            await self.memory.store(
                self.user_id,
                f"goal_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                {
                    "original_text": goal_text,
                    "parsed": parsed,
                    "created_at": datetime.utcnow().isoformat()
                }
            )

            return {
                "success": True,
                "original": goal_text,
                "parsed": parsed,
                "message": f"Goal understood! I've broken '{parsed.get('goal_title', goal_text)}' into {len(parsed.get('suggested_tasks', []))} actionable tasks."
            }

        except Exception as e:
            return {
                "success": False,
                "original": goal_text,
                "error": str(e),
                "message": "I couldn't parse that goal. Try being more specific about what you want to achieve and by when."
            }

    async def create_from_goal(self, parsed_goal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create project and tasks from a parsed goal.

        Returns the created project and tasks.
        """
        # Create project
        project = Project(
            id=generate_id(),
            userId=self.user_id,
            name=parsed_goal.get("suggested_project_name", "New Project"),
            description=parsed_goal.get("goal_description", "")
        )
        self.db.add(project)
        self.db.flush()  # Get project ID

        # Create tasks
        created_tasks = []
        for i, task_data in enumerate(parsed_goal.get("suggested_tasks", [])):
            task = Task(
                id=generate_id(),
                userId=self.user_id,
                projectId=project.id,
                title=task_data.get("title", f"Task {i+1}"),
                priority=task_data.get("priority", 3),  # Use integer priority
                estimatedMinutes=task_data.get("estimated_minutes", 60),
                status=TaskStatus.PENDING
            )
            self.db.add(task)
            created_tasks.append(task)

        # Set deadline if specified
        if parsed_goal.get("deadline"):
            try:
                deadline = datetime.fromisoformat(parsed_goal["deadline"])
                for task in created_tasks:
                    task.dueDate = deadline
            except ValueError:
                pass

        self.db.commit()

        return {
            "project": {
                "id": project.id,
                "name": project.name
            },
            "tasks": [{"id": t.id, "title": t.title} for t in created_tasks],
            "message": f"Created project '{project.name}' with {len(created_tasks)} tasks!"
        }

    async def get_daily_plan(self) -> Dict[str, Any]:
        """
        Generate the daily plan: "Good morning! Here's your day..."

        Considers:
        - Today's calendar
        - Due dates
        - Priority scores
        - User's peak productivity hours
        - Energy patterns from Shadow
        """
        now = datetime.utcnow()
        today_end = now.replace(hour=23, minute=59, second=59)

        # Get all active tasks
        tasks = self.db.query(Task).filter(
            Task.userId == self.user_id,
            Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS])
        ).all()

        # Prioritize tasks
        prioritized = self.scheduler.prioritize_tasks(tasks, self.user_id, self.db)

        # Get focus recommendations
        focus_recs = self.scheduler.get_focus_recommendations(self.user_id, self.db)

        # Get Shadow insights if available
        shadow_insight = None
        try:
            shadow = ShadowAnalyzerService(self.db)
            shadow_data = await shadow.get_daily_insight(self.user_id)
            if shadow_data:
                shadow_insight = getattr(shadow_data, "insight", None)
        except Exception:
            pass

        # Build daily plan
        top_3_tasks = prioritized[:3] if prioritized else []
        overdue = [t for t in prioritized if t["task"].dueDate and t["task"].dueDate < now]
        due_today = [t for t in prioritized if t["task"].dueDate and now <= t["task"].dueDate <= today_end]

        # Generate greeting based on time
        hour = now.hour
        if hour < 12:
            greeting = "Good morning"
        elif hour < 17:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"

        # Build message
        plan_parts = [f"{greeting}! Here's your focus for today:"]

        if overdue:
            plan_parts.append(f"\n⚠️ **{len(overdue)} overdue task(s)** need attention!")

        if due_today:
            plan_parts.append(f"\n📅 **{len(due_today)} task(s) due today**")

        if top_3_tasks:
            plan_parts.append("\n\n**Your top priorities:**")
            for i, item in enumerate(top_3_tasks, 1):
                task = item["task"]
                score = item["priority_score"]
                plan_parts.append(f"{i}. {task.title} (priority: {score:.0f})")

        if focus_recs.get("peak_productivity_hours"):
            peak_hours = focus_recs["peak_productivity_hours"]
            plan_parts.append(f"\n\n⚡ **Peak hours:** {', '.join(f'{h}:00' for h in peak_hours[:2])}")

        if shadow_insight:
            plan_parts.append(f"\n\n🌓 **Insight:** {shadow_insight}")

        return {
            "greeting": greeting,
            "message": "\n".join(plan_parts),
            "top_tasks": [
                {
                    "id": item["task"].id,
                    "title": item["task"].title,
                    "priority_score": item["priority_score"],
                    "recommendation": item["recommendation"]
                }
                for item in top_3_tasks
            ],
            "overdue_count": len(overdue),
            "due_today_count": len(due_today),
            "total_active": len(tasks),
            "peak_hours": focus_recs.get("peak_productivity_hours", []),
            "shadow_insight": shadow_insight,
            "generated_at": now.isoformat()
        }

    async def ask(self, question: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Ask the Brain anything. It knows your tasks, goals, patterns.

        Examples:
            "What should I work on?"
            "Am I on track to finish my project?"
            "When should I schedule deep work?"
            "Help me break down this task"
        """
        # Gather context
        tasks = self.db.query(Task).filter(
            Task.userId == self.user_id,
            Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS])
        ).limit(20).all()

        projects = self.db.query(Project).filter(
            Project.userId == self.user_id
        ).limit(10).all()

        # Get memory context
        memories = await self.memory.get_recent(self.user_id, limit=5)

        # Build context for AI
        context_parts = []

        if tasks:
            task_list = "\n".join([f"- [{t.status.value}] {t.title} (priority: {t.priority})" for t in tasks[:10]])
            context_parts.append(f"Current tasks:\n{task_list}")

        if projects:
            project_list = "\n".join([f"- {p.name}" for p in projects])
            context_parts.append(f"Active projects:\n{project_list}")

        if memories:
            memory_summary = "\n".join([f"- {m.get('key', 'memory')}: {str(m.get('value', ''))[:100]}" for m in memories])
            context_parts.append(f"Recent memory:\n{memory_summary}")

        full_context = "\n\n".join(context_parts)

        # Get prompt from external file (no hardcoding)
        prompt = get_prompt("ask", "prompt", context=full_context, question=question)

        try:
            # Use configured AI provider (no hardcoded models)
            provider = get_ai_provider()
            answer = await provider.generate(prompt, max_tokens=1024)

            return {
                "success": True,
                "question": question,
                "answer": answer,
                "context_used": {
                    "tasks": len(tasks),
                    "projects": len(projects),
                    "memories": len(memories)
                }
            }

        except Exception as e:
            return {
                "success": False,
                "question": question,
                "error": str(e),
                "answer": "I'm having trouble thinking right now. Try again in a moment."
            }

    async def suggest_next_action(self) -> Dict[str, Any]:
        """
        What should the user do RIGHT NOW?

        Considers:
        - Current time and energy
        - Task priorities
        - Recent activity
        - Calendar
        """
        # Get prioritized tasks
        tasks = self.db.query(Task).filter(
            Task.userId == self.user_id,
            Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS])
        ).all()

        if not tasks:
            return {
                "action": "add_goal",
                "message": "You have no active tasks! What would you like to accomplish?",
                "suggestion": "Tell me a goal and I'll help break it down."
            }

        prioritized = self.scheduler.prioritize_tasks(tasks, self.user_id, self.db)

        if not prioritized:
            return {
                "action": "review",
                "message": "All caught up! Review your goals or add something new.",
                "suggestion": None
            }

        top_task = prioritized[0]

        # Check if something is in progress
        in_progress = [t for t in tasks if t.status == TaskStatus.IN_PROGRESS]
        if in_progress:
            return {
                "action": "continue",
                "message": f"Continue working on: {in_progress[0].title}",
                "task": {
                    "id": in_progress[0].id,
                    "title": in_progress[0].title
                },
                "suggestion": "You have work in progress. Focus on finishing it!"
            }

        return {
            "action": "start",
            "message": f"Start: {top_task['task'].title}",
            "task": {
                "id": top_task["task"].id,
                "title": top_task["task"].title,
                "priority_score": top_task["priority_score"]
            },
            "reasoning": top_task["recommendation"],
            "suggestion": "This is your highest priority. Start the timer and focus!"
        }

    async def capture(self, input_text: str, create_item: bool = False) -> Dict[str, Any]:
        """
        AI-First Capture: Auto-categorize any input to the right type.

        The Brain understands what you're saying and creates the right item:
        - "I have an idea for..." → Idea
        - "My goal is..." → Plan/Goal
        - "Note to self..." → Note
        - "I need to..." → Task
        - "Strategy for..." → Custom type (if exists)

        Args:
            input_text: Natural language input from user
            create_item: If True, create the item. If False, just classify.

        Returns:
            Classified input with suggested type and extracted content
        """
        # Ensure user has default types
        ensure_default_item_types(self.user_id, self.db)

        # Get user's available types
        item_types = self.db.query(ItemType).filter(
            ItemType.userId == self.user_id
        ).all()

        type_names = [t.name for t in item_types]
        type_map = {t.name.lower(): t for t in item_types}

        # Get prompt from external file (no hardcoding)
        prompt = get_prompt(
            "capture", "classify",
            input=input_text,
            types=', '.join(type_names)
        )

        try:
            # Use configured AI provider (no hardcoded models)
            provider = get_ai_provider()
            response_text = await provider.generate(prompt, max_tokens=512)

            # Parse JSON
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0]
            else:
                json_str = response_text

            parsed = json.loads(json_str.strip())

            # Find the matching type
            type_name = parsed.get("type", "Notes").lower()
            item_type = type_map.get(type_name) or type_map.get("notes")

            result = {
                "success": True,
                "original": input_text,
                "classified": {
                    "type": item_type.name if item_type else "Notes",
                    "typeId": item_type.id if item_type else None,
                    "title": parsed.get("title", input_text[:100]),
                    "content": parsed.get("content", input_text),
                    "confidence": parsed.get("confidence", 0.8),
                    "reasoning": parsed.get("reasoning", "")
                }
            }

            # Create item if requested
            if create_item and item_type:
                knowledge_item = KnowledgeItem(
                    id=generate_id(),
                    userId=self.user_id,
                    typeId=item_type.id,
                    title=parsed.get("title", input_text[:100]),
                    content=parsed.get("content", input_text),
                    item_metadata={
                        "source": "brain-capture",
                        "confidence": parsed.get("confidence", 0.8),
                        "original_input": input_text
                    },
                    completed=False
                )
                self.db.add(knowledge_item)
                self.db.commit()
                self.db.refresh(knowledge_item)

                result["created"] = {
                    "id": knowledge_item.id,
                    "type": item_type.name,
                    "title": knowledge_item.title
                }
                result["message"] = f"Created {item_type.name}: {knowledge_item.title}"

            else:
                result["message"] = f"Would create {result['classified']['type']}: {result['classified']['title']}"

            return result

        except Exception as e:
            return {
                "success": False,
                "original": input_text,
                "error": str(e),
                "message": "Couldn't classify that input. Try being more specific."
            }

    async def get_knowledge_summary(self) -> Dict[str, Any]:
        """
        Get summary of all knowledge items by type.

        Returns counts and recent items for each type.
        """
        # Ensure defaults exist
        ensure_default_item_types(self.user_id, self.db)

        item_types = self.db.query(ItemType).filter(
            ItemType.userId == self.user_id
        ).all()

        summary = {
            "types": [],
            "total_items": 0
        }

        for item_type in item_types:
            items = self.db.query(KnowledgeItem).filter(
                KnowledgeItem.userId == self.user_id,
                KnowledgeItem.typeId == item_type.id
            ).order_by(KnowledgeItem.createdAt.desc()).limit(5).all()

            type_summary = {
                "type": item_type.name,
                "typeId": item_type.id,
                "icon": item_type.icon,
                "color": item_type.color,
                "count": self.db.query(KnowledgeItem).filter(
                    KnowledgeItem.userId == self.user_id,
                    KnowledgeItem.typeId == item_type.id
                ).count(),
                "recent": [{"id": i.id, "title": i.title} for i in items]
            }
            summary["types"].append(type_summary)
            summary["total_items"] += type_summary["count"]

        return summary
