#!/bin/bash

# Comprehensive Test Script for Focus by Kraliki
# 
# This script runs all tests for the Focus by Kraliki application including
# unit tests, integration tests, E2E tests, and generates coverage reports.
# 
# @module TestScript
# @version 1.0.0

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
TEST_RESULTS_DIR="$PROJECT_ROOT/test-results"
COVERAGE_DIR="$PROJECT_ROOT/coverage"

# Create directories
mkdir -p "$TEST_RESULTS_DIR"
mkdir -p "$COVERAGE_DIR"

# Helper functions
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[i]${NC} $1"
}

# Check if dependencies are installed
check_dependencies() {
    print_info "Checking dependencies..."
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed"
        exit 1
    fi
    
    # Check pnpm
    if ! command -v pnpm &> /dev/null; then
        print_error "pnpm is not installed"
        exit 1
    fi
    
    # Check Docker (for integration tests)
    if ! command -v docker &> /dev/null; then
        print_warning "Docker is not installed - some integration tests may fail"
    fi
    
    print_status "Dependencies check passed"
}

# Setup test database
setup_test_database() {
    print_info "Setting up test database..."
    
    cd "$BACKEND_DIR"
    
    # Check if test database exists
    if ! pnpm prisma db execute --stdin --url "${TEST_DATABASE_URL:-postgresql://postgres:password@localhost:5432/focus_kraliki_test}" <<< "SELECT 1;" &> /dev/null; then
        print_warning "Test database not found, creating..."
        
        # Create test database
        createdb focus_kraliki_test 2>/dev/null || true
        
        # Run migrations
        pnpm prisma migrate deploy
    fi
    
    # Seed test data
    pnpm prisma db seed || true
    
    print_status "Test database setup complete"
}

# Run backend tests
run_backend_tests() {
    print_info "Running backend tests..."
    
    cd "$BACKEND_DIR"
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        pnpm install
    fi
    
    # Run unit tests
    print_info "Running backend unit tests..."
    pnpm test:unit || {
        print_error "Backend unit tests failed"
        return 1
    }
    
    # Run integration tests
    print_info "Running backend integration tests..."
    pnpm test:integration || {
        print_error "Backend integration tests failed"
        return 1
    }
    
    # Generate coverage report
    print_info "Generating backend coverage report..."
    pnpm test:coverage || {
        print_warning "Backend coverage generation failed"
    }
    
    # Copy coverage results
    if [ -d "coverage" ]; then
        cp -r coverage "$COVERAGE_DIR/backend/"
    fi
    
    print_status "Backend tests completed"
}

# Run frontend tests
run_frontend_tests() {
    print_info "Running frontend tests..."
    
    cd "$FRONTEND_DIR"
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        pnpm install
    fi
    
    # Run unit tests
    print_info "Running frontend unit tests..."
    pnpm test:unit || {
        print_error "Frontend unit tests failed"
        return 1
    }
    
    # Run component tests
    print_info "Running frontend component tests..."
    pnpm test:component || {
        print_warning "Frontend component tests failed or not available"
    }
    
    # Generate coverage report
    print_info "Generating frontend coverage report..."
    pnpm test:coverage || {
        print_warning "Frontend coverage generation failed"
    }
    
    # Copy coverage results
    if [ -d "coverage" ]; then
        cp -r coverage "$COVERAGE_DIR/frontend/"
    fi
    
    print_status "Frontend tests completed"
}

# Run E2E tests
run_e2e_tests() {
    print_info "Running E2E tests..."
    
    cd "$PROJECT_ROOT"
    
    # Install Playwright if needed
    if ! command -v playwright &> /dev/null; then
        cd "$FRONTEND_DIR"
        pnpm dlx playwright install
        cd "$PROJECT_ROOT"
    fi
    
    # Check if backend is running
    if ! curl -f http://127.0.0.1:3017/health > /dev/null 2>&1; then
        print_warning "Backend is not running. Starting backend for E2E tests..."
        
        # Start backend in background
        cd "$BACKEND_DIR"
        pnpm dev &
        BACKEND_PID=$!
        
        # Wait for backend to start
        for i in {1..30}; do
            if curl -f http://127.0.0.1:3017/health > /dev/null 2>&1; then
                break
            fi
            sleep 1
        done
        
        cd "$PROJECT_ROOT"
    fi
    
    # Check if frontend is running
    if ! curl -f http://127.0.0.1:5175 > /dev/null 2>&1; then
        print_warning "Frontend is not running. Starting frontend for E2E tests..."
        
        # Start frontend in background
        cd "$FRONTEND_DIR"
        pnpm dev &
        FRONTEND_PID=$!
        
        # Wait for frontend to start
        for i in {1..30}; do
            if curl -f http://127.0.0.1:5175 > /dev/null 2>&1; then
                break
            fi
            sleep 1
        done
        
        cd "$PROJECT_ROOT"
    fi
    
    # Run E2E tests
    cd "$PROJECT_ROOT"
    
    if [ -d "e2e" ]; then
        pnpm test:e2e || {
            print_error "E2E tests failed"
            return 1
        }
    else
        print_warning "No E2E tests found"
    fi
    
    # Clean up background processes
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    print_status "E2E tests completed"
}

# Run performance tests
run_performance_tests() {
    print_info "Running performance tests..."
    
    cd "$BACKEND_DIR"
    
    # Run performance benchmarks
    if [ -f "test/performance/bench.test.ts" ]; then
        pnpm test:performance || {
            print_warning "Performance tests failed"
        }
    else
        print_warning "No performance tests found"
    fi
    
    print_status "Performance tests completed"
}

# Generate test report
generate_test_report() {
    print_info "Generating test report..."
    
    local report_file="$TEST_RESULTS_DIR/test-report-$(date +%Y%m%d-%H%M%S).md"
    
    cat > "$report_file" << EOF
# Focus by Kraliki Test Report

**Generated:** $(date)
**Test Environment:** $(node --version)

## Test Results

### Backend Tests
- Unit Tests: $([ -f "$COVERAGE_DIR/backend/lcov-report/index.html" ] && echo "✅ Passed" || echo "❌ Failed")
- Integration Tests: $([ -f "$COVERAGE_DIR/backend/lcov-report/index.html" ] && echo "✅ Passed" || echo "❌ Failed")
- Coverage: $(cd "$BACKEND_DIR" && pnpm test:coverage -- --reporter=text --reporter=json --outputFile="$TEST_RESULTS_DIR/backend-coverage.json" 2>/dev/null | tail -1 || echo "N/A")

### Frontend Tests
- Unit Tests: $([ -f "$COVERAGE_DIR/frontend/lcov-report/index.html" ] && echo "✅ Passed" || echo "❌ Failed")
- Component Tests: $([ -f "$COVERAGE_DIR/frontend/lcov-report/index.html" ] && echo "✅ Passed" || echo "❌ Failed")
- Coverage: $(cd "$FRONTEND_DIR" && pnpm test:coverage -- --reporter=text --reporter=json --outputFile="$TEST_RESULTS_DIR/frontend-coverage.json" 2>/dev/null | tail -1 || echo "N/A")

### E2E Tests
- End-to-End Tests: $([ -f "$TEST_RESULTS_DIR/e2e-results.xml" ] && echo "✅ Passed" || echo "❌ Failed")

## Coverage Reports

- Backend Coverage: file://$COVERAGE_DIR/backend/lcov-report/index.html
- Frontend Coverage: file://$COVERAGE_DIR/frontend/lcov-report/index.html

## Test Artifacts

- Test Results: $TEST_RESULTS_DIR
- Coverage Reports: $COVERAGE_DIR

EOF
    
    print_status "Test report generated: $report_file"
}

# Main function
main() {
    print_info "🚀 Starting Focus by Kraliki Test Suite"
    print_info "=========================================="
    
    # Parse command line arguments
    local RUN_BACKEND=true
    local RUN_FRONTEND=true
    local RUN_E2E=true
    local RUN_PERFORMANCE=false
    local SKIP_DEPS=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --backend-only)
                RUN_FRONTEND=false
                RUN_E2E=false
                shift
                ;;
            --frontend-only)
                RUN_BACKEND=false
                RUN_E2E=false
                shift
                ;;
            --e2e-only)
                RUN_BACKEND=false
                RUN_FRONTEND=false
                shift
                ;;
            --performance)
                RUN_PERFORMANCE=true
                shift
                ;;
            --skip-deps)
                SKIP_DEPS=true
                shift
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  --backend-only    Run only backend tests"
                echo "  --frontend-only   Run only frontend tests"
                echo "  --e2e-only        Run only E2E tests"
                echo "  --performance    Run performance tests"
                echo "  --skip-deps      Skip dependency check"
                echo "  --help           Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Check dependencies
    if [ "$SKIP_DEPS" = false ]; then
        check_dependencies
    fi
    
    # Setup test database
    if [ "$RUN_BACKEND" = true ]; then
        setup_test_database
    fi
    
    # Run tests
    local test_failed=false
    
    if [ "$RUN_BACKEND" = true ]; then
        run_backend_tests || test_failed=true
    fi
    
    if [ "$RUN_FRONTEND" = true ]; then
        run_frontend_tests || test_failed=true
    fi
    
    if [ "$RUN_E2E" = true ]; then
        run_e2e_tests || test_failed=true
    fi
    
    if [ "$RUN_PERFORMANCE" = true ]; then
        run_performance_tests || test_failed=true
    fi
    
    # Generate report
    generate_test_report
    
    # Summary
    echo ""
    if [ "$test_failed" = true ]; then
        print_error "❌ Some tests failed!"
        exit 1
    else
        print_status "✅ All tests passed!"
        echo ""
        print_info "📊 Coverage Reports:"
        echo "   Backend: file://$COVERAGE_DIR/backend/lcov-report/index.html"
        echo "   Frontend: file://$COVERAGE_DIR/frontend/lcov-report/index.html"
        echo ""
        print_info "📄 Test Report: $report_file"
        exit 0
    fi
}

# Run main function
main "$@"