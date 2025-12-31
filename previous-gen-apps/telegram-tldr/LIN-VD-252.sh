#!/bin/bash
# Verification script for LIN-VD-252: TL;DR Content Subscription Service

set -e

echo "======================================"
echo "Verifying LIN-VD-252: TL;DR Content Subscription Service"
echo "======================================"
echo ""

# Check for required service files
echo "1. Checking service files..."

FILES=(
    "app/services/news_aggregator.py"
    "app/services/tts.py"
    "app/services/newsletter.py"
)

all_files_exist=true
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file exists"
    else
        echo "  ✗ $file missing"
        all_files_exist=false
    fi
done

if [ "$all_files_exist" = false ]; then
    echo ""
    echo "❌ FAILED: Required service files are missing"
    exit 1
fi

echo ""
echo "2. Checking key functions in news_aggregator.py..."
KEY_FUNCTIONS=(
    "fetch_topic_news"
    "subscribe_newsletter"
    "unsubscribe_newsletter"
    "is_newsletter_subscriber"
    "get_user_news_topics"
    "set_user_news_topics"
    "set_newsletter_time"
    "get_newsletter_time"
    "get_all_newsletter_subscribers"
)

all_functions_exist=true
for func in "${KEY_FUNCTIONS[@]}"; do
    if grep -q "async def $func" app/services/news_aggregator.py; then
        echo "  ✓ $func function exists"
    else
        echo "  ✗ $func function missing"
        all_functions_exist=false
    fi
done

echo ""
echo "3. Checking key functions in tts.py..."
TTS_FUNCTIONS=(
    "text_to_speech"
    "cleanup_old_audio"
)

for func in "${TTS_FUNCTIONS[@]}"; do
    if grep -q "async def $func" app/services/tts.py; then
        echo "  ✓ $func function exists"
    else
        echo "  ✗ $func function missing"
        all_functions_exist=false
    fi
done

echo ""
echo "4. Checking key functions in newsletter.py..."
NEWSLETTER_FUNCTIONS=(
    "generate_newsletter"
    "get_newsletter_stats"
)

for func in "${NEWSLETTER_FUNCTIONS[@]}"; do
    if grep -q "async def $func" app/services/newsletter.py; then
        echo "  ✓ $func function exists"
    else
        echo "  ✗ $func function missing"
        all_functions_exist=false
    fi
done

echo ""
echo "5. Checking Telegram bot newsletter commands..."
BOT_COMMANDS=(
    "cmd_news"
    "_handle_newsletter_subscribe"
    "_handle_newsletter_unsubscribe"
    "_handle_newsletter_topics"
    "_handle_newsletter_time"
    "_handle_newsletter_now"
)

for cmd in "${BOT_COMMANDS[@]}"; do
    if grep -q "$cmd" app/services/bot.py; then
        echo "  ✓ $cmd handler exists"
    else
        echo "  ✗ $cmd handler missing"
        all_functions_exist=false
    fi
done

echo ""
echo "6. Checking scheduler newsletter integration..."
if grep -q "_check_newsletter_schedules" app/services/scheduler.py; then
    echo "  ✓ Newsletter scheduler check exists"
else
    echo "  ✗ Newsletter scheduler check missing"
    all_functions_exist=false
fi

if grep -q "_send_newsletter" app/services/scheduler.py; then
    echo "  ✓ Newsletter send function exists"
else
    echo "  ✗ Newsletter send function missing"
    all_functions_exist=false
fi

echo ""
echo "7. Checking config settings..."
CONFIG_SETTINGS=(
    "newsletter_price_stars"
    "newsletter_hours_to_fetch"
    "newsletter_max_articles"
)

for setting in "${CONFIG_SETTINGS[@]}"; do
    if grep -q "$setting" app/core/config.py; then
        echo "  ✓ $setting config exists"
    else
        echo "  ✗ $setting config missing"
        all_functions_exist=false
    fi
done

echo ""
echo "8. Checking dependencies in pyproject.toml..."
DEPS=(
    "feedparser"
    "gTTS"
)

for dep in "${DEPS[@]}"; do
    if grep -q "$dep" pyproject.toml; then
        echo "  ✓ $dep dependency added"
    else
        echo "  ✗ $dep dependency missing"
        all_functions_exist=false
    fi
done

echo ""
echo "9. Checking main.py imports..."
IMPORTS=(
    "from app.services.news_aggregator import news_aggregator"
    "from app.services.newsletter import newsletter"
    "from app.services.tts import tts"
)

for import_line in "${IMPORTS[@]}"; do
    if grep -q "$import_line" app/main.py; then
        echo "  ✓ $import_line"
    else
        echo "  ✗ Import missing: $import_line"
        all_functions_exist=false
    fi
done

echo ""
echo "10. Checking main.py service initialization..."
if grep -q "await news_aggregator.connect(buffer.redis)" app/main.py; then
    echo "  ✓ news_aggregator initialized"
else
    echo "  ✗ news_aggregator initialization missing"
    all_functions_exist=false
fi

if grep -q "await tts.connect(buffer.redis)" app/main.py; then
    echo "  ✓ tts initialized"
else
    echo "  ✗ tts initialization missing"
    all_functions_exist=false
fi

echo ""
echo "======================================"
if [ "$all_functions_exist" = true ]; then
    echo "✅ PASSED: All verification checks passed"
    echo ""
    echo "TL;DR Content Subscription Service features implemented:"
    echo "  • Daily digest generation from news sources (RSS feeds)"
    echo "  • Audio synthesis (TTS) for audio newsletters"
    echo "  • Telegram delivery channel (newsletter commands)"
    echo "  • Newsletter scheduler for daily delivery"
    echo "  • Subscription management with Telegram Stars"
    echo ""
    exit 0
else
    echo "❌ FAILED: Some verification checks failed"
    echo ""
    echo "Please review the failed checks above."
    exit 1
fi
