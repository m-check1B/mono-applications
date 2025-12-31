#!/bin/bash
# Focus by Kraliki - Run Tests
# Runs both backend and frontend tests

set -e

echo "🧪 Focus by Kraliki - Running Tests"
echo "============================="
echo ""

# Run backend tests
echo "Running backend tests..."
cd backend

if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
fi

if [ -d "tests" ]; then
    TEST_PROFILE="${FOCUS_TEST_PROFILE:-beta}"
    PYTEST_ARGS=()
    export DATABASE_URL="${DATABASE_URL:-sqlite:///./focus_kraliki.db}"
    export TEST_DATABASE_URL="${TEST_DATABASE_URL:-sqlite:///./test_focus_kraliki.db}"
    if [ "$TEST_PROFILE" = "full" ]; then
        TEST_TARGETS=(tests/)
    else
        # Beta gate: unit + stable smoke tests (skip heavy integration/perf).
        TEST_TARGETS=(tests/unit tests/test_adapter_smoke.py tests/test_projects_and_ai_scheduler_smoke.py tests/test_events.py tests/test_events_inmemory_subscribe.py tests/test_module_metrics.py)
        PYTEST_ARGS+=(-c pytest.beta.ini)
    fi

    if ! pytest "${PYTEST_ARGS[@]}" "${TEST_TARGETS[@]}"; then
        exit_code=$?
        if [ "$exit_code" -eq 5 ]; then
            echo "⚠️  Pytest found no tests to run"
        else
            exit "$exit_code"
        fi
    fi
else
    echo "⚠️  No backend tests found yet"
fi

cd ..

# Run frontend tests
echo ""
echo "Running frontend tests..."
cd frontend

if [ -f "package.json" ] && grep -q '"test"' package.json; then
    pnpm test
else
    echo "⚠️  No frontend tests configured yet"
fi

cd ..

echo ""
echo "✅ Test run complete!"
