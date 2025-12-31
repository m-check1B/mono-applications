"""LLM-powered chat summarization service using Gemini."""
import google.generativeai as genai
import json
import logging

from app.core.config import settings
from app.services.language import (
    detect_dominant_language,
    get_language_name,
    get_summary_language_prompt,
)

logger = logging.getLogger(__name__)

# Initialize client (lazy)
_model = None


def get_model():
    global _model
    if _model is None:
        genai.configure(api_key=settings.gemini_api_key)
        _model = genai.GenerativeModel(settings.gemini_model)
    return _model


# Summary length configurations
SUMMARY_LENGTH_CONFIG = {
    "short": {
        "max_tokens": 300,
        "instruction": "Be extremely brief. 2-3 bullet points max per section. Skip minor topics.",
    },
    "medium": {
        "max_tokens": 600,
        "instruction": "Be concise but thorough. Cover main topics with key details.",
    },
    "long": {
        "max_tokens": 1000,
        "instruction": "Be comprehensive. Include context, quotes, and nuanced details.",
    },
}


def get_length_tokens(length: str) -> int:
    """Get max output tokens for a summary length."""
    return SUMMARY_LENGTH_CONFIG.get(length, SUMMARY_LENGTH_CONFIG["medium"])["max_tokens"]


# Standard summary prompt template (length-aware, language-aware)
SUMMARY_PROMPT_TEMPLATE = """You are a chat summarizer. Analyze these Telegram group messages and create a summary.

LENGTH INSTRUCTION: {length_instruction}
LANGUAGE INSTRUCTION: {language_instruction}

GUIDELINES:
- Focus on substance, ignore small talk and greetings
- Extract actionable information
- Note any unanswered questions

OUTPUT FORMAT (use this exact structure):

**Topics Discussed:**
• [Topic 1]
• [Topic 2]
• [Topic 3]

**Key Points:**
• [Important point 1]
• [Important point 2]

**Links Shared:**
• [URL or "None"]

**Unanswered Questions:**
• [Question or "None"]

**Activity:** [X] messages from [Y] users

---
MESSAGES TO SUMMARIZE:
{messages}
"""

# Enhanced summary prompt with thread/topic detection (single-pass)
SUMMARY_WITH_THREADS_PROMPT = """You are a chat summarizer specialized in detecting conversation threads.

Analyze these Telegram group messages and create a thread-aware summary.

LENGTH INSTRUCTION: {length_instruction}
LANGUAGE INSTRUCTION: {language_instruction}

ANALYSIS TASK:
1. Identify distinct conversation threads/topics (2-5 main threads)
2. Note which users participated in each thread
3. Detect if messages are replies or continuations of previous topics
4. Rate thread importance: 🔴 High (active, many participants), 🟡 Medium, 🟢 Low

OUTPUT FORMAT:

**🧵 {thread_count} Conversation Threads**

**[Thread 1 Name]** 🔴
_Active participants: @user1, @user2_
• Key point 1
• Key point 2
{{if unanswered}}❓ Open question: [question]{{/if}}

**[Thread 2 Name]** 🟡
_Active participants: @user3_
• Key point

**📎 Links Shared:**
• [URL] — context
• Or "None shared"

**💬 Activity:** [X] messages from [Y] users across {thread_count} threads

---
MESSAGES TO SUMMARIZE:
{messages}
"""

# Enhanced topic detection prompt
TOPIC_DETECTION_PROMPT = """Analyze these chat messages and identify distinct conversation topics/threads.

TASK:
1. Identify 2-5 main conversation topics or threads
2. For each topic, list which messages (by index) belong to it
3. Identify the main participants in each topic
4. Rate each topic's importance (high/medium/low)

OUTPUT FORMAT (return ONLY valid JSON, no other text):
{{
  "topics": [
    {{
      "name": "Topic name (brief, 2-5 words)",
      "description": "What this conversation thread is about",
      "message_indices": [0, 1, 4, 7],
      "participants": ["user1", "user2"],
      "importance": "high|medium|low",
      "has_action_items": true|false,
      "has_questions": true|false
    }}
  ],
  "off_topic_indices": [2, 3, 5]
}}

MESSAGES:
{messages}

Return only valid JSON."""

# Topic-based summary prompt
TOPIC_SUMMARY_PROMPT = """Create a topic-organized summary of these chat messages.

DETECTED TOPICS:
{topics_json}

MESSAGES:
{messages}

OUTPUT FORMAT:

**📊 {topic_count} Topics Detected**

For each topic (ordered by importance):

**🔷 [Topic Name]** ({importance})
_Participants: @user1, @user2_
• Key point 1
• Key point 2
{if has_questions}• ❓ Unanswered: [question]{/if}
{if has_action_items}• ✅ Action: [action item]{/if}

**🔗 Links Shared:**
• [URLs or "None"]

**📈 Activity:** {message_count} messages from {user_count} users

Write in a conversational yet professional tone. Be concise."""


async def summarize_messages(
    messages: list[dict],
    length: str = "medium",
    language: str = "auto",
    detect_threads: bool = True,
) -> str:
    """Generate a summary of chat messages using Gemini.

    Args:
        messages: List of message dicts with 'user', 'text', 'ts' keys
        length: Summary length preference ('short', 'medium', 'long')
        language: Target language code ('auto', 'en', 'cs', etc.)
        detect_threads: Enable thread/topic detection for richer summaries

    Returns:
        Markdown-formatted summary string
    """
    if not messages:
        return "No messages to summarize."

    # Validate length parameter
    if length not in SUMMARY_LENGTH_CONFIG:
        length = "medium"

    # Format messages for the prompt
    formatted = []
    users = set()
    for msg in messages:
        user = msg.get("user", "Unknown")
        text = msg.get("text", "")
        users.add(user)
        formatted.append(f"[{user}]: {text}")

    # Limit to max messages
    max_msgs = settings.max_messages_per_summary
    messages_text = "\n".join(formatted[-max_msgs:])

    # Get length config
    length_config = SUMMARY_LENGTH_CONFIG[length]
    max_tokens = length_config["max_tokens"]
    length_instruction = length_config["instruction"]

    # Get language instruction
    if language == "auto":
        # Detect dominant language from messages
        detected_lang = detect_dominant_language(messages)
        language_instruction = get_summary_language_prompt(detected_lang)
        output_lang = detected_lang
    else:
        language_instruction = get_summary_language_prompt(language)
        output_lang = language

    # Call Gemini
    model = get_model()

    # Use thread-aware prompt for messages with enough content (15+ messages)
    # and when thread detection is enabled
    use_thread_detection = detect_threads and len(messages) >= 15

    try:
        if use_thread_detection:
            # Use enhanced thread-detection prompt
            # Estimate thread count based on user diversity
            estimated_threads = min(5, max(2, len(users) // 2))
            response = await model.generate_content_async(
                SUMMARY_WITH_THREADS_PROMPT.format(
                    messages=messages_text,
                    length_instruction=length_instruction,
                    language_instruction=language_instruction,
                    thread_count=estimated_threads,
                ),
                generation_config=genai.GenerationConfig(
                    max_output_tokens=max_tokens + 200,  # Extra tokens for thread info
                    temperature=0.3,
                )
            )
        else:
            # Use standard prompt for smaller message sets
            response = await model.generate_content_async(
                SUMMARY_PROMPT_TEMPLATE.format(
                    messages=messages_text,
                    length_instruction=length_instruction,
                    language_instruction=language_instruction,
                ),
                generation_config=genai.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.3,
                )
            )

        summary = response.text

        # Add metadata footer with length and language indicator
        length_emoji = {"short": "📝", "medium": "📄", "long": "📚"}.get(length, "📄")
        lang_name = get_language_name(output_lang)
        thread_indicator = " • 🧵 threads detected" if use_thread_detection else ""
        summary += f"\n\n_{length_emoji} {length.capitalize()} summary in {lang_name} • {len(messages)} messages from {len(users)} users{thread_indicator}_"

        return summary

    except Exception as e:
        return f"Error generating summary: {str(e)}"


async def detect_topics(messages: list[dict]) -> dict | None:
    """Detect conversation topics/threads in messages.

    Uses AI to identify distinct conversation threads, participants,
    and importance levels.

    Args:
        messages: List of message dicts with 'user', 'text', 'ts' keys

    Returns:
        Dict with 'topics' list or None on failure
    """
    if not messages or len(messages) < 3:
        return None

    # Format messages with indices
    formatted = []
    for i, msg in enumerate(messages):
        user = msg.get("user", "Unknown")
        text = msg.get("text", "")
        formatted.append(f"{i}. [{user}]: {text}")

    max_msgs = settings.max_messages_per_summary
    messages_text = "\n".join(formatted[-max_msgs:])

    model = get_model()

    try:
        response = await model.generate_content_async(
            TOPIC_DETECTION_PROMPT.format(messages=messages_text),
            generation_config=genai.GenerationConfig(
                max_output_tokens=800,
                temperature=0.1,  # Low temp for structured output
            )
        )

        result_text = response.text.strip()

        # Remove markdown code blocks if present
        if result_text.startswith("```"):
            result_text = result_text.split("\n", 1)[1]
            result_text = result_text.rsplit("```", 1)[0]

        return json.loads(result_text)

    except (json.JSONDecodeError, Exception) as e:
        logger.warning(f"Topic detection failed: {e}")
        return None


async def summarize_with_topics(messages: list[dict]) -> str:
    """Generate an enhanced summary with topic detection.

    First detects distinct conversation threads, then creates
    a topic-organized summary.

    Args:
        messages: List of message dicts with 'user', 'text', 'ts' keys

    Returns:
        Markdown-formatted topic-organized summary
    """
    if not messages:
        return "No messages to summarize."

    # For small message counts, use simple summary
    if len(messages) < 10:
        return await summarize_messages(messages)

    # Detect topics first
    topics_data = await detect_topics(messages)

    if not topics_data or not topics_data.get("topics"):
        # Fall back to standard summary
        return await summarize_messages(messages)

    # Format messages
    formatted = []
    users = set()
    for msg in messages:
        user = msg.get("user", "Unknown")
        text = msg.get("text", "")
        users.add(user)
        formatted.append(f"[{user}]: {text}")

    max_msgs = settings.max_messages_per_summary
    messages_text = "\n".join(formatted[-max_msgs:])

    model = get_model()

    try:
        # Generate topic-organized summary
        response = await model.generate_content_async(
            TOPIC_SUMMARY_PROMPT.format(
                topics_json=json.dumps(topics_data["topics"], indent=2),
                messages=messages_text,
                topic_count=len(topics_data["topics"]),
                message_count=len(messages),
                user_count=len(users)
            ),
            generation_config=genai.GenerationConfig(
                max_output_tokens=1200,
                temperature=0.3,
            )
        )

        summary = response.text

        # Add metadata footer
        summary += f"\n\n_Analyzed {len(messages)} messages, detected {len(topics_data['topics'])} topics_"

        return summary

    except Exception as e:
        logger.error(f"Topic summary generation failed: {e}")
        # Fall back to standard summary
        return await summarize_messages(messages)


async def get_topic_stats(messages: list[dict]) -> dict:
    """Get topic statistics for messages.

    Returns topic names, participant counts, and message distribution.
    Useful for analytics and UI display.

    Args:
        messages: List of message dicts

    Returns:
        Dict with topic statistics
    """
    topics_data = await detect_topics(messages)

    if not topics_data or not topics_data.get("topics"):
        return {
            "topic_count": 0,
            "topics": [],
            "total_messages": len(messages),
        }

    topics = topics_data["topics"]

    # Sort by importance
    importance_order = {"high": 0, "medium": 1, "low": 2}
    topics.sort(key=lambda t: importance_order.get(t.get("importance", "low"), 2))

    return {
        "topic_count": len(topics),
        "topics": [
            {
                "name": t["name"],
                "description": t.get("description", ""),
                "participants": t.get("participants", []),
                "message_count": len(t.get("message_indices", [])),
                "importance": t.get("importance", "medium"),
                "has_action_items": t.get("has_action_items", False),
                "has_questions": t.get("has_questions", False),
            }
            for t in topics
        ],
        "off_topic_count": len(topics_data.get("off_topic_indices", [])),
        "total_messages": len(messages),
    }


async def estimate_cost(message_count: int) -> float:
    """Estimate API cost for summarization.

    Gemini 2.0 Flash pricing (as of late 2024):
    - Free tier: 1500 requests/day
    - Paid: $0.075 / 1M input tokens, $0.30 / 1M output tokens

    This is ~50% cheaper than GPT-4o-mini!
    """
    input_tokens = message_count * 100
    output_tokens = 500

    input_cost = (input_tokens / 1_000_000) * 0.075
    output_cost = (output_tokens / 1_000_000) * 0.30

    return input_cost + output_cost
