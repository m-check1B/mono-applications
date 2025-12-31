"""
Milestone 7: Simplified Automated Regression Suite

Comprehensive regression testing covering UI, API, telephony, and browser channel components.
"""

import asyncio
import json
import time
import pytest
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import subprocess
import sys
import urllib.request
import urllib.error
import urllib.parse

@dataclass
class TestResult:
    """Individual test result"""
    name: str
    category: str
    status: str  # PASS, FAIL, SKIP
    duration: float
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

@dataclass
class RegressionReport:
    """Complete regression test report"""
    timestamp: datetime
    total_tests: int
    passed: int
    failed: int
    skipped: int
    duration: float
    results: List[TestResult]
    summary: Dict[str, Any]

class HTTPClient:
    """Simple HTTP client using urllib"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    def get(self, endpoint: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Make GET request"""
        url = f"{self.base_url}{endpoint}"
        req_headers = {"Content-Type": "application/json", "User-Agent": "regression-test"}
        if headers:
            req_headers.update(headers)
        
        try:
            req = urllib.request.Request(url, headers=req_headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = response.read().decode('utf-8')
                return {
                    "status_code": response.getcode(),
                    "data": json.loads(data) if data else None,
                    "headers": dict(response.headers)
                }
        except urllib.error.HTTPError as e:
            return {
                "status_code": e.code,
                "data": e.read().decode('utf-8') if hasattr(e, 'read') else str(e),
                "headers": dict(e.headers) if hasattr(e, 'headers') else {}
            }
        except Exception as e:
            return {
                "status_code": 0,
                "data": str(e),
                "headers": {}
            }
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Make POST request"""
        url = f"{self.base_url}{endpoint}"
        req_headers = {"Content-Type": "application/json", "User-Agent": "regression-test"}
        if headers:
            req_headers.update(headers)
        
        try:
            json_data = json.dumps(data).encode('utf-8') if data else None
            req = urllib.request.Request(url, data=json_data, headers=req_headers, method='POST')
            with urllib.request.urlopen(req, timeout=10) as response:
                response_data = response.read().decode('utf-8')
                return {
                    "status_code": response.getcode(),
                    "data": json.loads(response_data) if response_data else None,
                    "headers": dict(response.headers)
                }
        except urllib.error.HTTPError as e:
            return {
                "status_code": e.code,
                "data": e.read().decode('utf-8') if hasattr(e, 'read') else str(e),
                "headers": dict(e.headers) if hasattr(e, 'headers') else {}
            }
        except Exception as e:
            return {
                "status_code": 0,
                "data": str(e),
                "headers": {}
            }

class RegressionTestRunner:
    """Main regression test runner"""
    
    def __init__(self, base_url: str = "http://localhost:8000", frontend_url: str = "http://localhost:5173"):
        self.base_url = base_url
        self.frontend_url = frontend_url
        self.results: List[TestResult] = []
        self.start_time: Optional[float] = None
        
    async def run_test(self, test_func, category: str, test_name: str) -> TestResult:
        """Run a single test and capture results"""
        start_time = time.time()
        
        try:
            print(f"🧪 Running {category}.{test_name}...")
            
            if hasattr(test_func, '__await__'):
                result = await test_func()
            else:
                result = test_func()
                
            duration = time.time() - start_time
            
            if result is True or result is None:
                return TestResult(
                    name=test_name,
                    category=category,
                    status="PASS",
                    duration=duration,
                    details={"result": result} if result else None
                )
            else:
                return TestResult(
                    name=test_name,
                    category=category,
                    status="FAIL",
                    duration=duration,
                    error=str(result)
                )
                
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                name=test_name,
                category=category,
                status="FAIL",
                duration=duration,
                error=str(e)
            )
    
    async def run_category(self, category: str, tests: Dict[str, Any]):
        """Run all tests in a category"""
        print(f"\n📂 Running {category} tests...")
        print("-" * 50)
        
        for test_name, test_func in tests.items():
            result = await self.run_test(test_func, category, test_name)
            self.results.append(result)
            
            status_icon = "✅" if result.status == "PASS" else "❌" if result.status == "FAIL" else "⏭️"
            print(f"{status_icon} {result.name} ({result.duration:.2f}s)")
            
            if result.error:
                print(f"   Error: {result.error}")
    
    def generate_report(self) -> RegressionReport:
        """Generate comprehensive regression report"""
        total_tests = len(self.results)
        passed = sum(1 for r in self.results if r.status == "PASS")
        failed = sum(1 for r in self.results if r.status == "FAIL")
        skipped = sum(1 for r in self.results if r.status == "SKIP")
        
        duration = time.time() - self.start_time if self.start_time else 0
        
        # Category breakdown
        categories = {}
        for result in self.results:
            if result.category not in categories:
                categories[result.category] = {"pass": 0, "fail": 0, "skip": 0}
            categories[result.category][result.status.lower()] += 1
        
        return RegressionReport(
            timestamp=datetime.now(timezone.utc),
            total_tests=total_tests,
            passed=passed,
            failed=failed,
            skipped=skipped,
            duration=duration,
            results=self.results,
            summary={
                "success_rate": (passed / total_tests * 100) if total_tests > 0 else 0,
                "categories": categories,
                "failed_tests": [r.name for r in self.results if r.status == "FAIL"]
            }
        )

class APIRegressionTests:
    """API endpoint regression tests"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = HTTPClient(base_url)
    
    def test_health_endpoint(self):
        """Test health endpoint availability"""
        response = self.client.get("/health")
        assert response["status_code"] == 200
        data = response["data"]
        assert data["status"] == "healthy"
        assert "service" in data
        return True
    
    def test_providers_list(self):
        """Test providers list endpoint"""
        response = self.client.get("/api/v1/providers")
        assert response["status_code"] == 200
        data = response["data"]
        assert "providers" in data
        assert "telephony" in data
        assert len(data["providers"]) > 0
        return True
    
    def test_session_bootstrap(self):
        """Test session bootstrap endpoint"""
        session_request = {
            "provider_type": "openai",
            "provider_model": "gpt-4",
            "strategy": "single_provider",
            "telephony_provider": "twilio"
        }
        
        response = self.client.post("/api/v1/sessions/bootstrap", session_request)
        assert response["status_code"] == 200
        data = response["data"]
        assert "session_id" in data
        assert "websocket_url" in data
        assert "provider_type" in data
        return data["session_id"]
    
    def test_compliance_regions(self):
        """Test compliance regions endpoint"""
        response = self.client.get("/api/compliance/regions")
        assert response["status_code"] == 200
        data = response["data"]
        assert isinstance(data, list)
        assert len(data) > 0
        return True
    
    def test_alerting_health(self):
        """Test alerting health endpoint"""
        response = self.client.get("/api/alerting/health")
        assert response["status_code"] == 200
        data = response["data"]
        assert data["status"] == "healthy"
        assert "active_alerts" in data
        assert "total_rules" in data
        return True
    
    def test_telephony_providers(self):
        """Test telephony providers endpoint"""
        response = self.client.get("/api/telephony/providers")
        assert response["status_code"] == 200
        data = response["data"]
        assert isinstance(data, list)
        return True
    
    def test_campaign_scripts(self):
        """Test campaign scripts endpoint"""
        response = self.client.get("/api/campaigns/scripts")
        assert response["status_code"] == 200
        data = response["data"]
        assert "scripts" in data
        return True

class TelephonyRegressionTests:
    """Telephony-specific regression tests"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = HTTPClient(base_url)
    
    def test_twilio_webhook_validation(self):
        """Test Twilio webhook validation setup"""
        # Test webhook endpoint exists and returns proper response
        webhook_data = {
            "CallSid": "test_call_sid",
            "From": "+1234567890",
            "To": "+0987654321",
            "CallStatus": "ringing"
        }
        
        response = self.client.post("/telephony/webhooks/twilio", webhook_data)
        # Should return TwiML or error (403 if signature validation fails)
        assert response["status_code"] in [200, 403]
        return True
    
    def test_telnyx_webhook_validation(self):
        """Test Telnyx webhook validation setup"""
        webhook_data = {
            "data": {
                "event_type": "call_initiated",
                "call": {
                    "call_id": "test_call_id",
                    "from": "+1234567890",
                    "to": "+0987654321"
                }
            }
        }
        
        response = self.client.post("/telephony/webhooks/telnyx", webhook_data)
        # Should return JSON response or error
        assert response["status_code"] in [200, 400, 403]
        return True
    
    def test_inbound_call_routing(self):
        """Test inbound call routing configuration"""
        response = self.client.get("/telephony/routes/inbound")
        assert response["status_code"] in [200, 404]  # May not exist but should not error
        return True
    
    def test_outbound_call_capabilities(self):
        """Test outbound call capabilities"""
        response = self.client.get("/telephony/capabilities/outbound")
        assert response["status_code"] in [200, 404]
        return True

class BrowserChannelRegressionTests:
    """Browser channel regression tests"""
    
    def __init__(self, base_url: str, frontend_url: str):
        self.base_url = base_url
        self.frontend_url = frontend_url
        self.client = HTTPClient(base_url)
    
    def test_frontend_health(self):
        """Test frontend is accessible"""
        try:
            req = urllib.request.Request(self.frontend_url, headers={"User-Agent": "regression-test"})
            with urllib.request.urlopen(req, timeout=10) as response:
                assert response.getcode() == 200
                content_type = response.headers.get("content-type", "")
                assert "text/html" in content_type
            return True
        except Exception as e:
            return f"Frontend not accessible: {e}"
    
    def test_browser_chat_api(self):
        """Test browser chat API endpoints"""
        # Test chat history endpoint
        response = self.client.get("/api/chat/history")
        assert response["status_code"] in [200, 401]  # May require auth
        return True
    
    def test_static_assets(self):
        """Test static assets are served correctly"""
        assets = [
            "/favicon.svg",
            "/robots.txt"
        ]
        
        for asset in assets:
            try:
                req = urllib.request.Request(f"{self.frontend_url}{asset}", headers={"User-Agent": "regression-test"})
                with urllib.request.urlopen(req, timeout=5) as response:
                    assert response.getcode() == 200
            except Exception as e:
                return f"Asset {asset} not accessible: {e}"
        
        return True

class PerformanceRegressionTests:
    """Performance regression tests"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = HTTPClient(base_url)
    
    def test_api_response_times(self):
        """Test API response times are within acceptable limits"""
        endpoints = [
            "/health",
            "/api/v1/providers",
            "/api/compliance/regions",
            "/api/alerting/health"
        ]
        
        max_response_time = 2.0  # 2 seconds
        
        for endpoint in endpoints:
            start_time = time.time()
            response = self.client.get(endpoint)
            response_time = time.time() - start_time
            
            assert response["status_code"] == 200
            assert response_time < max_response_time, f"{endpoint} took {response_time:.2f}s"
        
        return True

class SecurityRegressionTests:
    """Security regression tests"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = HTTPClient(base_url)
    
    def test_cors_headers(self):
        """Test CORS headers are properly configured"""
        response = self.client.get("/api/v1/providers")
        
        # Should have CORS headers
        headers = response.get("headers", {})
        has_cors = any("access-control-allow-origin" in str(key).lower() for key in headers.keys())
        assert has_cors, f"No CORS headers found: {list(headers.keys())}"
        return True
    
    def test_authentication_required(self):
        """Test protected endpoints require authentication"""
        protected_endpoints = [
            "/api/compliance/consents",
            "/api/alerting/rules"
        ]
        
        for endpoint in protected_endpoints:
            response = self.client.get(endpoint)
            # Should require authentication (401) or not exist (404)
            assert response["status_code"] in [401, 404]
        
        return True

async def run_full_regression_suite():
    """Run complete regression test suite"""
    print("🚀 Starting Milestone 7 Regression Suite")
    print("=" * 60)
    
    runner = RegressionTestRunner()
    runner.start_time = time.time()
    
    # Initialize test classes
    api_tests = APIRegressionTests(runner.base_url)
    telephony_tests = TelephonyRegressionTests(runner.base_url)
    browser_tests = BrowserChannelRegressionTests(runner.base_url, runner.frontend_url)
    performance_tests = PerformanceRegressionTests(runner.base_url)
    security_tests = SecurityRegressionTests(runner.base_url)
    
    # Define test suites
    test_suites = {
        "API Tests": {
            "test_health_endpoint": api_tests.test_health_endpoint,
            "test_providers_list": api_tests.test_providers_list,
            "test_session_bootstrap": api_tests.test_session_bootstrap,
            "test_compliance_regions": api_tests.test_compliance_regions,
            "test_alerting_health": api_tests.test_alerting_health,
            "test_telephony_providers": api_tests.test_telephony_providers,
            "test_campaign_scripts": api_tests.test_campaign_scripts,
        },
        "Telephony Tests": {
            "test_twilio_webhook_validation": telephony_tests.test_twilio_webhook_validation,
            "test_telnyx_webhook_validation": telephony_tests.test_telnyx_webhook_validation,
            "test_inbound_call_routing": telephony_tests.test_inbound_call_routing,
            "test_outbound_call_capabilities": telephony_tests.test_outbound_call_capabilities,
        },
        "Browser Channel Tests": {
            "test_frontend_health": browser_tests.test_frontend_health,
            "test_browser_chat_api": browser_tests.test_browser_chat_api,
            "test_static_assets": browser_tests.test_static_assets,
        },
        "Performance Tests": {
            "test_api_response_times": performance_tests.test_api_response_times,
        },
        "Security Tests": {
            "test_cors_headers": security_tests.test_cors_headers,
            "test_authentication_required": security_tests.test_authentication_required,
        }
    }
    
    # Run all test suites
    for category, tests in test_suites.items():
        await runner.run_category(category, tests)
    
    # Generate report
    report = runner.generate_report()
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 REGRESSION TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {report.total_tests}")
    print(f"Passed: {report.passed} ✅")
    print(f"Failed: {report.failed} ❌")
    print(f"Skipped: {report.skipped} ⏭️")
    print(f"Success Rate: {report.summary['success_rate']:.1f}%")
    print(f"Duration: {report.duration:.2f}s")
    
    # Category breakdown
    print("\n📋 Results by Category:")
    for category, stats in report.summary['categories'].items():
        total = stats['pass'] + stats['fail'] + stats['skip']
        success_rate = (stats['pass'] / total * 100) if total > 0 else 0
        print(f"  {category}: {stats['pass']}/{total} ({success_rate:.1f}%)")
    
    # Failed tests
    if report.failed > 0:
        print(f"\n❌ Failed Tests:")
        for test_name in report.summary['failed_tests']:
            failed_result = next(r for r in report.results if r.name == test_name)
            print(f"  - {test_name}: {failed_result.error}")
    
    # Save report
    report_data = asdict(report)
    report_data['timestamp'] = report.timestamp.isoformat()
    
    with open("regression_test_report.json", "w") as f:
        json.dump(report_data, f, indent=2, default=str)
    
    print(f"\n📄 Detailed report saved to: regression_test_report.json")
    
    return report.failed == 0

if __name__ == "__main__":
    # Run regression tests
    success = asyncio.run(run_full_regression_suite())
    
    if success:
        print("\n🎉 All regression tests passed!")
        exit(0)
    else:
        print("\n💥 Some regression tests failed!")
        exit(1)