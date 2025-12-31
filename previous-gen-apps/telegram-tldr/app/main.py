"""TL;DR Bot - FastAPI Application."""

import logging
from contextlib import asynccontextmanager
from datetime import datetime, UTC

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse

from app.core.config import settings
from app.services.analytics import analytics
from app.services.bot import bot, process_update, remove_webhook, setup_webhook
from app.services.buffer import buffer
from app.services.content_subscription import content_subscription
from app.services.news_aggregator import news_aggregator
from app.services.newsletter import newsletter
from app.services.scheduler import scheduler
from app.services.tts import tts

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown."""
    # Startup
    logger.info("Starting TL;DR Bot...")

    # Validate payment configuration
    if settings.subscription_price_stars <= 0:
        logger.error(
            "PAYMENT: SUBSCRIPTION_PRICE_STARS must be > 0. "
            "Check your .env file and set a valid price."
        )
        raise RuntimeError("SUBSCRIPTION_PRICE_STARS must be > 0")
    if settings.newsletter_price_stars <= 0:
        logger.error(
            "PAYMENT: NEWSLETTER_PRICE_STARS must be > 0. "
            "Check your .env file and set a valid price."
        )
        raise RuntimeError("NEWSLETTER_PRICE_STARS must be > 0")

    logger.info(
        f"Payment config: Subscription={settings.subscription_price_stars} Stars, "
        f"Newsletter={settings.newsletter_price_stars} Stars"
    )

    # Connect to Redis
    await buffer.connect()
    await analytics.connect()

    # Share Redis connection with other services
    await content_subscription.connect(buffer.redis)
    await news_aggregator.connect(buffer.redis)
    await tts.connect(buffer.redis)

    logger.info("Redis connected")

    # Set up webhook if URL configured
    if settings.telegram_webhook_url:
        # Require webhook secret for security
        if not settings.telegram_webhook_secret:
            logger.error(
                "SECURITY: TELEGRAM_WEBHOOK_SECRET is required when using webhooks. "
                "Generate a random string and set it in .env"
            )
            raise RuntimeError("TELEGRAM_WEBHOOK_SECRET is required for webhook mode")
        webhook_url = f"{settings.telegram_webhook_url}/webhook"
        await setup_webhook(webhook_url, secret_token=settings.telegram_webhook_secret)
        logger.info(f"Webhook configured at {webhook_url} with secret validation")
    else:
        logger.warning("No webhook URL configured - bot won't receive updates")

    # Start scheduled digest service
    scheduler.set_bot(bot)
    await scheduler.start()
    logger.info("Digest scheduler started")

    yield

    # Shutdown
    logger.info("Shutting down...")
    await scheduler.stop()
    await remove_webhook()
    await buffer.close()
    await analytics.close()
    await bot.session.close()


app = FastAPI(
    title=settings.app_name,
    description="Telegram bot that summarizes busy group chats",
    version="0.1.0",
    lifespan=lifespan,
)


# ============================================================
# ROUTES
# ============================================================


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "app": settings.app_name, "version": "0.1.0"}


@app.get("/health")
async def health():
    """Detailed health check."""
    redis_ok = False
    try:
        if buffer.redis:
            await buffer.redis.ping()
            redis_ok = True
    except Exception as e:
        logger.warning("Redis health check failed: %s", e)

    return {
        "status": "healthy" if redis_ok else "degraded",
        "redis": "connected" if redis_ok else "disconnected",
    }


# ============================================================
# ANALYTICS DASHBOARD
# ============================================================


def _verify_dashboard_token(token: str | None) -> bool:
    """Verify dashboard access token (uses webhook secret for simplicity)."""
    if not settings.telegram_webhook_secret:
        return False
    return token == settings.telegram_webhook_secret


@app.get("/api/analytics")
async def get_analytics(token: str = Query(..., description="Dashboard access token")):
    """Get analytics data as JSON for the dashboard."""
    if not _verify_dashboard_token(token):
        raise HTTPException(status_code=403, detail="Invalid access token")

    data = await analytics.get_dashboard_data()
    return data


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(token: str = Query(..., description="Dashboard access token")):
    """Render the analytics dashboard HTML page."""
    if not _verify_dashboard_token(token):
        raise HTTPException(status_code=403, detail="Invalid access token")

    html_content = _get_dashboard_html(token)
    return HTMLResponse(content=html_content)


def _get_dashboard_html(token: str) -> str:
    """Generate the dashboard HTML with embedded Chart.js."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TL;DR Bot Analytics</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f0f0f;
            color: #e0e0e0;
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        h1 {{ color: #fff; margin-bottom: 8px; font-size: 28px; }}
        .subtitle {{ color: #888; margin-bottom: 24px; font-size: 14px; }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 32px;
        }}
        .stat-card {{
            background: #1a1a1a;
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #2a2a2a;
        }}
        .stat-label {{ color: #888; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; }}
        .stat-value {{ font-size: 32px; font-weight: 600; color: #fff; margin: 8px 0; }}
        .stat-delta {{ font-size: 12px; }}
        .stat-delta.positive {{ color: #22c55e; }}
        .stat-delta.negative {{ color: #ef4444; }}
        .chart-section {{
            background: #1a1a1a;
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #2a2a2a;
            margin-bottom: 24px;
        }}
        .chart-title {{ color: #fff; font-size: 16px; margin-bottom: 16px; }}
        .chart-container {{ height: 300px; position: relative; }}
        .two-col {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 24px; }}
        .commands-list {{ list-style: none; }}
        .commands-list li {{
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid #2a2a2a;
        }}
        .commands-list li:last-child {{ border-bottom: none; }}
        .cmd-name {{ color: #22c55e; font-family: monospace; }}
        .cmd-count {{ color: #fff; font-weight: 500; }}
        .errors-list {{ list-style: none; }}
        .errors-list li {{
            padding: 12px;
            background: #1f1f1f;
            border-radius: 8px;
            margin-bottom: 8px;
            font-size: 13px;
        }}
        .error-type {{ color: #ef4444; font-weight: 500; }}
        .error-time {{ color: #666; font-size: 11px; }}
        .loading {{ text-align: center; padding: 40px; color: #888; }}
        .refresh-btn {{
            background: #22c55e;
            color: #000;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            font-size: 13px;
        }}
        .refresh-btn:hover {{ background: #16a34a; }}
        .header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>TL;DR Bot Analytics</h1>
                <p class="subtitle" id="lastUpdated">Loading...</p>
            </div>
            <button class="refresh-btn" onclick="loadData()">Refresh</button>
        </div>

        <div class="stats-grid" id="statsGrid">
            <div class="stat-card"><div class="loading">Loading...</div></div>
        </div>

        <div class="chart-section">
            <h3 class="chart-title">Activity (Last 7 Days)</h3>
            <div class="chart-container">
                <canvas id="activityChart"></canvas>
            </div>
        </div>

        <div class="two-col">
            <div class="chart-section">
                <h3 class="chart-title">Command Usage</h3>
                <ul class="commands-list" id="commandsList">
                    <li class="loading">Loading...</li>
                </ul>
            </div>

            <div class="chart-section">
                <h3 class="chart-title">Recent Errors</h3>
                <ul class="errors-list" id="errorsList">
                    <li class="loading">Loading...</li>
                </ul>
            </div>
        </div>
    </div>

    <script>
        const API_URL = '/api/analytics?token={token}';
        let activityChart = null;

        function formatNumber(n) {{
            if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
            if (n >= 1000) return (n / 1000).toFixed(1) + 'K';
            return n.toString();
        }}

        function createStatCard(label, value, delta = null, suffix = '') {{
            let deltaHtml = '';
            if (delta !== null) {{
                const cls = delta >= 0 ? 'positive' : 'negative';
                const sign = delta >= 0 ? '+' : '';
                deltaHtml = `<div class="stat-delta ${{cls}}">${{sign}}${{delta}} today</div>`;
            }}
            const displayValue = (typeof value === 'number')
                ? `${{formatNumber(value)}}${{suffix}}`
                : value;
            return `
                <div class="stat-card">
                    <div class="stat-label">${{label}}</div>
                    <div class="stat-value">${{displayValue}}</div>
                    ${{deltaHtml}}
                </div>
            `;
        }}

        async function loadData() {{
            try {{
                const resp = await fetch(API_URL);
                if (!resp.ok) throw new Error('Failed to load');
                const data = await resp.json();
                renderDashboard(data);
            }} catch (e) {{
                console.error(e);
                document.getElementById('statsGrid').innerHTML = '<div class="stat-card"><div class="loading">Error loading data</div></div>';
            }}
        }}

        function renderDashboard(data) {{
            // Update timestamp
            const dt = new Date(data.generated_at);
            document.getElementById('lastUpdated').textContent = `Last updated: ${{dt.toLocaleString()}}`;

            // Stats cards
            const at = data.all_time;
            const td = data.today;
            const conv = data.conversion || { premium_chats: 0, free_chats: 0, conversion_rate: 0 };
            const convRate = `${{conv.conversion_rate.toFixed(1)}}%`;
            document.getElementById('statsGrid').innerHTML = `
                ${{createStatCard('Total Messages', at.messages_processed, td.messages_processed)}}
                ${{createStatCard('Summaries Generated', at.summaries_generated, td.summaries_generated)}}
                ${{createStatCard('Active Groups (Today)', td.active_chats)}}
                ${{createStatCard('All-Time Groups', at.unique_chats)}}
                ${{createStatCard('Unique Users', at.unique_users, td.active_users)}}
                ${{createStatCard('Premium Groups', conv.premium_chats)}}
                ${{createStatCard('Free Groups', conv.free_chats)}}
                ${{createStatCard('Conversion Rate', convRate)}}
                ${{createStatCard('Subscriptions', at.subscriptions_total, td.new_subscriptions)}}
                ${{createStatCard('Errors', at.errors_total, td.errors)}}
            `;

            // Activity chart
            const labels = data.trends_7d.map(d => d.date.slice(5)); // MM-DD
            const msgs = data.trends_7d.map(d => d.messages_processed);
            const sums = data.trends_7d.map(d => d.summaries_generated);
            const users = data.trends_7d.map(d => d.active_users);

            if (activityChart) activityChart.destroy();

            activityChart = new Chart(document.getElementById('activityChart'), {{
                type: 'line',
                data: {{
                    labels: labels,
                    datasets: [
                        {{
                            label: 'Messages',
                            data: msgs,
                            borderColor: '#22c55e',
                            backgroundColor: 'rgba(34, 197, 94, 0.1)',
                            tension: 0.3,
                            fill: true
                        }},
                        {{
                            label: 'Summaries',
                            data: sums,
                            borderColor: '#3b82f6',
                            backgroundColor: 'rgba(59, 130, 246, 0.1)',
                            tension: 0.3,
                            fill: true
                        }},
                        {{
                            label: 'Active Users',
                            data: users,
                            borderColor: '#f59e0b',
                            backgroundColor: 'rgba(245, 158, 11, 0.1)',
                            tension: 0.3,
                            fill: true
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            labels: {{ color: '#888' }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            grid: {{ color: '#2a2a2a' }},
                            ticks: {{ color: '#888' }}
                        }},
                        y: {{
                            grid: {{ color: '#2a2a2a' }},
                            ticks: {{ color: '#888' }}
                        }}
                    }}
                }}
            }});

            // Commands list
            const cmds = data.commands;
            const cmdsSorted = Object.entries(cmds).sort((a, b) => b[1] - a[1]);
            document.getElementById('commandsList').innerHTML = cmdsSorted
                .map(([cmd, count]) => `<li><span class="cmd-name">/${{cmd}}</span><span class="cmd-count">${{formatNumber(count)}}</span></li>`)
                .join('');

            // Errors list
            const errors = data.recent_errors;
            if (errors.length === 0) {{
                document.getElementById('errorsList').innerHTML = '<li style="color: #22c55e;">No recent errors</li>';
            }} else {{
                document.getElementById('errorsList').innerHTML = errors
                    .map(e => `<li><span class="error-type">${{e.type}}</span>: ${{e.details || 'No details'}}<div class="error-time">${{new Date(e.ts).toLocaleString()}}</div></li>`)
                    .join('');
            }}
        }}

        // Load on page ready
        loadData();
        // Auto-refresh every 60 seconds
        setInterval(loadData, 60000);
    </script>
</body>
</html>"""


@app.post("/webhook")
async def telegram_webhook(request: Request):
    """Handle incoming Telegram updates via webhook.

    Security: Validates X-Telegram-Bot-Api-Secret-Token header.
    If TELEGRAM_WEBHOOK_SECRET is not configured, webhook is disabled for security.
    """
    # Require secret token for webhook authentication (prevents forged updates)
    if not settings.telegram_webhook_secret:
        logger.error("Webhook called but TELEGRAM_WEBHOOK_SECRET not configured")
        raise HTTPException(status_code=503, detail="Webhook not configured")

    secret_header = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if secret_header != settings.telegram_webhook_secret:
        logger.warning("Invalid or missing webhook secret token")
        raise HTTPException(status_code=403, detail="Forbidden")

    try:
        update_data = await request.json()
        await process_update(update_data)
        return {"ok": True}
    except Exception:
        logger.exception("Webhook processing error")
        raise HTTPException(status_code=500, detail="Internal error")


# ============================================================
# STRIPE WEBHOOK
# ============================================================


from app.services.payments import payment_service


# ============================================================
# STRIPE SUCCESS/CANCEL CALLBACKS
# ============================================================


@app.get("/subscribe/success")
async def stripe_success(session_id: str = Query(..., description="Stripe checkout session ID")):
    """Handle successful Stripe checkout - redirect to Telegram bot."""
    return HTMLResponse(content=f"""<!DOCTYPE html>
<html>
<head>
    <title>Payment Successful - TL;DR Bot</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f0f0f;
            color: #e0e0e0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
        }}
        .container {{
            text-align: center;
            padding: 40px;
            max-width: 400px;
        }}
        .success-icon {{ font-size: 64px; margin-bottom: 20px; }}
        h1 {{ color: #22c55e; margin-bottom: 16px; }}
        p {{ color: #888; margin-bottom: 24px; }}
        a {{
            display: inline-block;
            background: #22c55e;
            color: #000;
            text-decoration: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 500;
        }}
        a:hover {{ background: #16a34a; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="success-icon">✅</div>
        <h1>Payment Successful!</h1>
        <p>Your Pro subscription is now active. Return to Telegram to start using unlimited summaries.</p>
        <a href="https://t.me/">Open Telegram</a>
    </div>
</body>
</html>""")


@app.get("/subscribe/cancel")
async def stripe_cancel():
    """Handle cancelled Stripe checkout - redirect to Telegram bot."""
    return HTMLResponse(content="""<!DOCTYPE html>
<html>
<head>
    <title>Payment Cancelled - TL;DR Bot</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f0f0f;
            color: #e0e0e0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
        }
        .container {
            text-align: center;
            padding: 40px;
            max-width: 400px;
        }
        .cancel-icon { font-size: 64px; margin-bottom: 20px; }
        h1 { color: #f59e0b; margin-bottom: 16px; }
        p { color: #888; margin-bottom: 24px; }
        a {
            display: inline-block;
            background: #3b82f6;
            color: #fff;
            text-decoration: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 500;
        }
        a:hover { background: #2563eb; }
    </style>
</head>
<body>
    <div class="container">
        <div class="cancel-icon">↩️</div>
        <h1>Payment Cancelled</h1>
        <p>No worries! You can try again anytime using /subscribe in the bot.</p>
        <a href="https://t.me/">Return to Telegram</a>
    </div>
</body>
</html>""")


@app.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events.

    Security: Validates webhook signature.
    """
    try:
        event = await payment_service.verify_stripe_webhook(request)
    except HTTPException as e:
        logger.error(f"Stripe webhook verification failed: {e.detail}")
        raise e

    event_type = event["type"]
    data = event["data"]["object"]

    logger.info(f"Stripe webhook received: {event_type}")

    try:
        if event_type == "checkout.session.completed":
            await handle_checkout_completed(data)
        elif event_type == "customer.subscription.created":
            await handle_subscription_created(data)
        elif event_type == "customer.subscription.updated":
            await handle_subscription_updated(data)
        elif event_type == "customer.subscription.deleted":
            await handle_subscription_cancelled(data)
        elif event_type == "invoice.payment_succeeded":
            await handle_payment_succeeded(data)
        elif event_type == "invoice.payment_failed":
            await handle_payment_failed(data)
        else:
            logger.info(f"Unhandled Stripe event type: {event_type}")

        return {"status": "received"}

    except Exception as e:
        logger.exception(f"Stripe webhook processing error: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing error")


async def handle_checkout_completed(session: dict):
    """Handle successful Stripe checkout session."""
    metadata = session.get("metadata", {})
    user_id = int(metadata.get("telegram_user_id", 0))
    tier = metadata.get("tier")

    if not user_id or not tier:
        logger.error(f"Invalid checkout session metadata: {metadata}")
        return

    # Subscription will be handled by subscription.created event
    logger.info(f"Checkout completed for user {user_id}, tier {tier}")


async def handle_subscription_created(subscription: dict):
    """Handle Stripe subscription creation."""
    metadata = subscription.get("metadata", {})
    user_id = int(metadata.get("telegram_user_id", 0))
    tier = metadata.get("tier")
    subscription_id = subscription.get("id")
    status = subscription.get("status")

    if not user_id or not tier:
        logger.error(f"Invalid subscription metadata: {metadata}")
        return

    # Store subscription in Redis
    await buffer.set_stripe_subscription(user_id, subscription_id, status)

    # Grant access based on tier
    if tier in ("pro", "content_pro"):
        await buffer.set_subscribed(user_id, months=1)

    logger.info(f"Subscription created: user {user_id}, tier {tier}, sub_id {subscription_id}")


async def handle_subscription_updated(subscription: dict):
    """Handle Stripe subscription updates."""
    metadata = subscription.get("metadata", {})
    user_id = int(metadata.get("telegram_user_id", 0))
    subscription_id = subscription.get("id")
    status = subscription.get("status")

    if not user_id:
        return

    # Update subscription status in Redis
    existing = await buffer.get_stripe_subscription(user_id)
    if existing:
        existing["status"] = status
        existing["updated_at"] = datetime.now(UTC).isoformat()
        await buffer.set_stripe_subscription(user_id, subscription_id, status)

    logger.info(f"Subscription updated: user {user_id}, status {status}")


async def handle_subscription_cancelled(subscription: dict):
    """Handle Stripe subscription cancellation."""
    metadata = subscription.get("metadata", {})
    user_id = int(metadata.get("telegram_user_id", 0))
    subscription_id = subscription.get("id")

    if not user_id:
        return

    # Mark subscription as cancelled in Redis
    existing = await buffer.get_stripe_subscription(user_id)
    if existing:
        existing["status"] = "canceled"
        existing["cancel_at"] = datetime.now(UTC).isoformat()
        await buffer.set_stripe_subscription(user_id, subscription_id, "canceled")

    # Don't immediately revoke access - let user finish billing period
    logger.info(f"Subscription cancelled: user {user_id}, sub_id {subscription_id}")


async def handle_payment_succeeded(invoice: dict):
    """Handle successful Stripe payment."""
    subscription = invoice.get("subscription")
    if subscription:
        logger.info(f"Payment succeeded for subscription {subscription}")


async def handle_payment_failed(invoice: dict):
    """Handle failed Stripe payment."""
    subscription_id = invoice.get("subscription")
    logger.warning(f"Payment failed for subscription {subscription_id}")

    # Mark subscription as past_due
    if subscription_id:
        # Find user by subscription_id and update status
        # This would require scanning Redis or storing subscription -> user mapping
        logger.info(f"Marking subscription {subscription_id} as past_due")


# ============================================================
# ERROR HANDLERS
# ============================================================


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(status_code=500, content={"error": "Internal server error"})


# ============================================================
# DEV MODE: Polling fallback
# ============================================================

if __name__ == "__main__":
    import asyncio

    async def run_polling():
        """Run bot in polling mode for development."""
        from app.services.bot import bot, dp

        logger.info("Starting in polling mode (development)...")

        # Connect Redis
        await buffer.connect()
        await analytics.connect()

        # Remove any existing webhook
        await bot.delete_webhook()

        # Start polling
        await dp.start_polling(bot)

    asyncio.run(run_polling())
