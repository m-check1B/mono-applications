"""
Speak by Kraliki - Voice Pipeline Router
WebSocket endpoint for real-time voice conversations
"""

import json
import logging
from uuid import UUID
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db, async_session
from app.core.auth import hash_magic_link_token
from app.models.employee import Employee
from app.models.conversation import Conversation
from app.models.survey import Survey
from app.models.company import Company
from app.models.department import Department
from app.models.alert import Alert
from app.services.ai_conversation import AIConversationService, DEFAULT_QUESTIONS
from app.services.analysis import AnalysisService
from app.services.usage_service import usage_service
from app.schemas.conversation import ConversationStart, ConversationComplete
from app.services.reach_voice import build_reach_client, ReachVoiceError
from app.core.config import settings

router = APIRouter(prefix="/speak/voice", tags=["voice"])

ai_service = AIConversationService()
analysis_service = AnalysisService()
logger = logging.getLogger(__name__)


def build_reach_prompt(
    employee_name: str,
    company_name: str,
    department_name: Optional[str],
    questions: list[dict],
    custom_prompt: Optional[str],
) -> str:
    question_lines = "\n".join(
        f"{idx + 1}. {q.get('question', '')}" for idx, q in enumerate(questions)
    )

    base_prompt = f"""Jsi Speak by Kraliki - hlasovy asistent pro mesicni check-in se zamestnancem.
Mluv cesky, prirozene a kratce (1-2 vety).
Ptej se jednu otazku po druhe a pockej na odpoved.
Neslibuj zmeny - pouze naslouchej a podkuj.

KONTEXT:
- Zamestnanec: {employee_name}
- Firma: {company_name}
- Oddeleni: {department_name or "Nezname"}

OTAZKY (v tomto poradi):
{question_lines}
"""

    if custom_prompt:
        base_prompt += f"\nDOPLNUJICI INSTRUKCE:\n{custom_prompt.strip()}\n"

    return base_prompt


@router.websocket("/ws/{token}")
async def voice_websocket(
    websocket: WebSocket,
    token: str,
):
    """
    WebSocket endpoint for real-time voice conversation.

    Protocol:
    1. Client connects with magic link token
    2. Server sends greeting
    3. Client sends audio/text messages
    4. Server responds with AI messages
    5. After completion, server triggers analysis

    Message format:
    {
        "type": "audio" | "text" | "end" | "fallback",
        "content": "...",
        "audio_data": "base64..." (for audio type)
    }
    """
    await websocket.accept()

    async with async_session() as db:
        try:
            # Hash the incoming token and look up by hash (tokens stored as hashes)
            token_hash = hash_magic_link_token(token)
            emp_result = await db.execute(
                select(Employee).where(Employee.magic_link_token == token_hash)
            )
            employee = emp_result.scalar_one_or_none()

            if not employee:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid or expired link"
                })
                await websocket.close()
                return

            if employee.magic_link_expires and employee.magic_link_expires < datetime.now(timezone.utc):
                await websocket.send_json({
                    "type": "error",
                    "message": "Link has expired"
                })
                await websocket.close()
                return

            # Get active conversation
            conv_result = await db.execute(
                select(Conversation)
                .where(Conversation.employee_id == employee.id)
                .where(Conversation.status.in_(["invited", "in_progress"]))
                .order_by(Conversation.created_at.desc())
                .limit(1)
            )
            conversation = conv_result.scalar_one_or_none()

            if not conversation:
                await websocket.send_json({
                    "type": "error",
                    "message": "No active survey for you"
                })
                await websocket.close()
                return

            # Get survey for questions
            survey_result = await db.execute(
                select(Survey).where(Survey.id == conversation.survey_id)
            )
            survey = survey_result.scalar_one()

            # Get company and department names
            company_result = await db.execute(
                select(Company).where(Company.id == employee.company_id)
            )
            company = company_result.scalar_one()

            dept_name = None
            if employee.department_id:
                dept_result = await db.execute(
                    select(Department).where(Department.id == employee.department_id)
                )
                dept = dept_result.scalar_one_or_none()
                dept_name = dept.name if dept else None

            # Initialize conversation state
            conversation.status = "in_progress"
            conversation.started_at = datetime.utcnow()
            conversation.transcript = []
            await db.commit()

            # Get questions (from survey or default)
            questions = survey.questions if survey.questions else DEFAULT_QUESTIONS
            current_question_idx = 0

            # Send greeting
            greeting = ai_service.get_greeting(employee.first_name)
            await websocket.send_json({
                "type": "ai_message",
                "content": greeting,
                "is_greeting": True
            })

            # Add greeting to transcript
            conversation.transcript.append({
                "role": "ai",
                "content": greeting,
                "timestamp": datetime.utcnow().isoformat()
            })

            # Send first question
            if questions:
                first_question = questions[0]["question"]
                await websocket.send_json({
                    "type": "ai_message",
                    "content": first_question,
                    "question_id": 0
                })
                conversation.transcript.append({
                    "role": "ai",
                    "content": first_question,
                    "timestamp": datetime.utcnow().isoformat()
                })

            await db.commit()

            # Conversation loop
            follow_up_count = 0
            max_follow_ups = questions[current_question_idx].get("follow_up_count", 1) if questions else 0
            use_text_mode = False

            while True:
                try:
                    # Receive message from client
                    data = await websocket.receive_json()
                    msg_type = data.get("type")
                    content = data.get("content", "")

                    if msg_type == "end":
                        # End conversation
                        break

                    if msg_type == "fallback":
                        # Switch to text mode
                        use_text_mode = True
                        conversation.fallback_to_text = True
                        conversation.fallback_reason = data.get("reason", "user_requested")
                        await websocket.send_json({
                            "type": "mode_changed",
                            "mode": "text"
                        })
                        continue

                    if msg_type == "text" or use_text_mode:
                        user_message = content
                    elif msg_type == "audio":
                        # In production, transcribe audio via Gemini STT
                        # For now, expect text in content
                        user_message = content

                    if not user_message:
                        continue

                    # Add user message to transcript
                    conversation.transcript.append({
                        "role": "user",
                        "content": user_message,
                        "timestamp": datetime.utcnow().isoformat()
                    })

                    # Determine if we should ask follow-up or move to next question
                    should_follow_up = (
                        follow_up_count < max_follow_ups and
                        len(user_message) > 20  # Only follow up on substantial answers
                    )

                    if should_follow_up:
                        # Generate follow-up response
                        current_q = questions[current_question_idx]["question"] if questions else ""
                        ai_response = await ai_service.generate_response(
                            employee_name=employee.first_name,
                            company_name=company.name,
                            department_name=dept_name or "",
                            current_question=current_q,
                            user_message=user_message,
                            conversation_history=conversation.transcript,
                            custom_prompt=survey.custom_system_prompt,
                        )
                        follow_up_count += 1
                    else:
                        # Move to next question
                        current_question_idx += 1
                        follow_up_count = 0

                        if current_question_idx >= len(questions):
                            # End of questions
                            ai_response = ai_service.get_farewell()
                            await websocket.send_json({
                                "type": "ai_message",
                                "content": ai_response,
                                "is_final": True
                            })
                            conversation.transcript.append({
                                "role": "ai",
                                "content": ai_response,
                                "timestamp": datetime.utcnow().isoformat()
                            })
                            break
                        else:
                            # Acknowledge and ask next question
                            max_follow_ups = questions[current_question_idx].get("follow_up_count", 1)
                            next_question = questions[current_question_idx]["question"]
                            ai_response = f"Diky za odpoved. {next_question}"

                    # Send AI response
                    await websocket.send_json({
                        "type": "ai_message",
                        "content": ai_response,
                        "question_id": current_question_idx
                    })

                    # Add to transcript
                    conversation.transcript.append({
                        "role": "ai",
                        "content": ai_response,
                        "timestamp": datetime.utcnow().isoformat()
                    })

                    await db.commit()

                except WebSocketDisconnect:
                    break
                except json.JSONDecodeError:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Invalid message format"
                    })
                    continue

            # Finalize conversation
            conversation.status = "completed"
            conversation.completed_at = datetime.utcnow()
            if conversation.started_at:
                duration = (conversation.completed_at - conversation.started_at).total_seconds()
                conversation.duration_seconds = int(duration)
                
                # Record usage
                await usage_service.record_usage(
                    db=db,
                    company_id=employee.company_id,
                    quantity=int(duration),
                    service_type="voice_minutes",
                    reference_id=str(conversation.id)
                )

            # Run analysis
            if conversation.transcript:
                analysis = analysis_service.analyze_transcript(conversation.transcript)
                conversation.sentiment_score = analysis["sentiment_score"]
                conversation.topics = analysis["topics"]
                conversation.flags = analysis["flags"]
                conversation.summary = analysis["summary"]

                # Generate alerts
                if analysis["flags"]:
                    alerts = analysis_service.generate_alerts(
                        conversation_id=str(conversation.id),
                        company_id=str(employee.company_id),
                        department_id=str(employee.department_id) if employee.department_id else None,
                        flags=analysis["flags"],
                        transcript=conversation.transcript,
                    )
                    for alert_data in alerts:
                        alert = Alert(
                            company_id=UUID(alert_data["company_id"]),
                            conversation_id=UUID(alert_data["conversation_id"]),
                            type=alert_data["type"],
                            severity=alert_data["severity"],
                            department_id=UUID(alert_data["department_id"]) if alert_data["department_id"] else None,
                            description=alert_data["description"],
                            trigger_keywords=alert_data["trigger_keywords"],
                        )
                        db.add(alert)

            # Update employee stats
            employee.vop_last_survey = datetime.utcnow()

            await db.commit()

            # Send completion message
            await websocket.send_json({
                "type": "completed",
                "message": "Conversation completed. Thank you!",
                "can_review_transcript": True
            })

        except Exception as e:
            await websocket.send_json({
                "type": "error",
                "message": f"An error occurred: {str(e)}"
            })
        finally:
            try:
                await websocket.close()
            except Exception:
                pass  # Connection already closed


@router.post("/start")
async def start_voice_conversation(
    token: str = Query(...),
    request: ConversationStart = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Initialize voice conversation (non-WebSocket start).
    Returns conversation info for client setup.
    """
    # Hash the incoming token and look up by hash
    token_hash = hash_magic_link_token(token)
    emp_result = await db.execute(
        select(Employee).where(Employee.magic_link_token == token_hash)
    )
    employee = emp_result.scalar_one_or_none()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired link"
        )

    if employee.magic_link_expires and employee.magic_link_expires < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Link has expired"
        )

    # Get active conversation
    conv_result = await db.execute(
        select(Conversation)
        .where(Conversation.employee_id == employee.id)
        .where(Conversation.status.in_(["invited", "in_progress"]))
        .order_by(Conversation.created_at.desc())
        .limit(1)
    )
    conversation = conv_result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active survey"
        )

    # Gather survey context for Reach voice sessions
    survey_result = await db.execute(
        select(Survey).where(Survey.id == conversation.survey_id)
    )
    survey = survey_result.scalar_one()

    company_result = await db.execute(
        select(Company).where(Company.id == employee.company_id)
    )
    company = company_result.scalar_one()

    dept_name = None
    if employee.department_id:
        dept_result = await db.execute(
            select(Department).where(Department.id == employee.department_id)
        )
        dept = dept_result.scalar_one_or_none()
        dept_name = dept.name if dept else None

    reach_client = build_reach_client()
    if reach_client:
        questions = survey.questions if survey.questions else DEFAULT_QUESTIONS
        system_prompt = build_reach_prompt(
            employee_name=employee.first_name,
            company_name=company.name,
            department_name=dept_name,
            questions=questions,
            custom_prompt=survey.custom_system_prompt,
        )
        metadata = {
            "conversation_id": str(conversation.id),
            "survey_id": str(survey.id),
            "employee_id": str(employee.id),
            "company_id": str(company.id),
            "employee_name": employee.first_name,
            "company_name": company.name,
            "department_name": dept_name,
            "mode": request.mode if request else "voice",
        }

        payload = {
            "provider_type": settings.reach_voice_provider_type,
            "strategy": settings.reach_voice_strategy,
            "system_prompt": system_prompt,
            "metadata": metadata,
        }

        try:
            reach_response = await reach_client.bootstrap_session(payload)
            conversation.status = "in_progress"
            conversation.started_at = datetime.utcnow()
            conversation.transcript = []
            await db.commit()

            return {
                "conversation_id": str(conversation.id),
                "employee_name": employee.first_name,
                "websocket_url": reach_response["websocket_url"],
                "reach": True,
                "reach_session_id": reach_response.get("session_id"),
                "mode": request.mode if request else "voice",
            }
        except ReachVoiceError as exc:
            logger.warning("Reach voice bootstrap failed, falling back to local", exc_info=exc)

    return {
        "conversation_id": str(conversation.id),
        "employee_name": employee.first_name,
        "websocket_url": f"/speak/voice/ws/{token}",
        "mode": request.mode if request else "voice",
    }


@router.post("/fallback-text")
async def switch_to_text(
    token: str = Query(...),
    reason: str = Query(default="user_requested"),
    db: AsyncSession = Depends(get_db)
):
    """Switch ongoing conversation to text mode."""
    # Hash the incoming token and look up by hash
    token_hash = hash_magic_link_token(token)
    emp_result = await db.execute(
        select(Employee).where(Employee.magic_link_token == token_hash)
    )
    employee = emp_result.scalar_one_or_none()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired link"
        )

    if employee.magic_link_expires and employee.magic_link_expires < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Link has expired"
        )

    conv_result = await db.execute(
        select(Conversation)
        .where(Conversation.employee_id == employee.id)
        .where(Conversation.status == "in_progress")
        .order_by(Conversation.created_at.desc())
        .limit(1)
    )
    conversation = conv_result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active conversation"
        )

    conversation.fallback_to_text = True
    conversation.fallback_reason = reason
    await db.commit()

    return {"message": "Switched to text mode", "conversation_id": str(conversation.id)}


@router.post("/complete")
async def complete_voice_conversation(
    payload: ConversationComplete,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Finalize a Reach-backed conversation and persist transcript."""
    token_hash = hash_magic_link_token(token)
    emp_result = await db.execute(
        select(Employee).where(Employee.magic_link_token == token_hash)
    )
    employee = emp_result.scalar_one_or_none()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired link"
        )

    if employee.magic_link_expires and employee.magic_link_expires < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Link has expired"
        )

    conv_result = await db.execute(
        select(Conversation)
        .where(Conversation.employee_id == employee.id)
        .where(Conversation.status.in_(["invited", "in_progress"]))
        .order_by(Conversation.created_at.desc())
        .limit(1)
    )
    conversation = conv_result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active conversation"
        )

    transcript = []
    for turn in payload.transcript:
        entry = {
            "role": turn.role,
            "content": turn.content,
            "timestamp": turn.timestamp.isoformat(),
        }
        if turn.redacted:
            entry["redacted"] = True
        transcript.append(entry)

    conversation.status = "completed"
    conversation.completed_at = datetime.utcnow()
    if not conversation.started_at:
        conversation.started_at = datetime.utcnow()
    conversation.transcript = transcript

    if payload.duration_seconds:
        conversation.duration_seconds = payload.duration_seconds
    elif conversation.started_at and conversation.completed_at:
        duration = (conversation.completed_at - conversation.started_at).total_seconds()
        conversation.duration_seconds = int(duration)

    if conversation.duration_seconds:
        await usage_service.record_usage(
            db=db,
            company_id=employee.company_id,
            quantity=int(conversation.duration_seconds),
            service_type="voice_minutes",
            reference_id=str(conversation.id)
        )

    if conversation.transcript:
        analysis = analysis_service.analyze_transcript(conversation.transcript)
        conversation.sentiment_score = analysis["sentiment_score"]
        conversation.topics = analysis["topics"]
        conversation.flags = analysis["flags"]
        conversation.summary = analysis["summary"]

        if analysis["flags"]:
            alerts = analysis_service.generate_alerts(
                conversation_id=str(conversation.id),
                company_id=str(employee.company_id),
                department_id=str(employee.department_id) if employee.department_id else None,
                flags=analysis["flags"],
                transcript=conversation.transcript,
            )
            for alert_data in alerts:
                alert = Alert(
                    company_id=UUID(alert_data["company_id"]),
                    conversation_id=UUID(alert_data["conversation_id"]),
                    type=alert_data["type"],
                    severity=alert_data["severity"],
                    department_id=UUID(alert_data["department_id"]) if alert_data["department_id"] else None,
                    description=alert_data["description"],
                    trigger_keywords=alert_data["trigger_keywords"],
                )
                db.add(alert)

    employee.vop_last_survey = datetime.utcnow()
    await db.commit()

    return {"success": True, "conversation_id": str(conversation.id)}
