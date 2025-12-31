"""
Milestone 6: Load Testing for Telephony System

Tests inbound/outbound call volume handling capacity and validates
performance under stress conditions.
"""

import asyncio
import time
import statistics
import json
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import aiohttp
import pytest

@dataclass
class LoadTestMetrics:
    """Metrics collected during load testing"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_per_second: float
    error_rate: float
    errors: List[str]

class LoadTestRunner:
    """Load testing runner for telephony endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.metrics = LoadTestMetrics(
            total_requests=0,
            successful_requests=0,
            failed_requests=0,
            avg_response_time=0.0,
            min_response_time=float('inf'),
            max_response_time=0.0,
            p95_response_time=0.0,
            p99_response_time=0.0,
            requests_per_second=0.0,
            error_rate=0.0,
            errors=[]
        )
        self.response_times = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a single HTTP request and record metrics"""
        start_time = time.time()
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self.session.request(method, url, **kwargs) as response:
                response_time = time.time() - start_time
                self.response_times.append(response_time)
                
                self.metrics.total_requests += 1
                
                if response.status < 400:
                    self.metrics.successful_requests += 1
                    return {
                        "status": "success",
                        "status_code": response.status,
                        "response_time": response_time,
                        "data": await response.json() if response.content_type == "application/json" else None
                    }
                else:
                    self.metrics.failed_requests += 1
                    error_msg = f"HTTP {response.status}: {await response.text()}"
                    self.metrics.errors.append(error_msg)
                    return {
                        "status": "error",
                        "status_code": response.status,
                        "response_time": response_time,
                        "error": error_msg
                    }
                    
        except Exception as e:
            response_time = time.time() - start_time
            self.response_times.append(response_time)
            self.metrics.total_requests += 1
            self.metrics.failed_requests += 1
            error_msg = f"Exception: {str(e)}"
            self.metrics.errors.append(error_msg)
            return {
                "status": "error",
                "response_time": response_time,
                "error": error_msg
            }
    
    def calculate_metrics(self, duration: float):
        """Calculate final metrics from collected data"""
        if self.response_times:
            self.metrics.avg_response_time = statistics.mean(self.response_times)
            self.metrics.min_response_time = min(self.response_times)
            self.metrics.max_response_time = max(self.response_times)
            self.metrics.p95_response_time = statistics.quantiles(self.response_times, n=20)[18]  # 95th percentile
            self.metrics.p99_response_time = statistics.quantiles(self.response_times, n=100)[98]  # 99th percentile
        
        self.metrics.requests_per_second = self.metrics.total_requests / duration if duration > 0 else 0
        self.metrics.error_rate = (self.metrics.failed_requests / self.metrics.total_requests * 100) if self.metrics.total_requests > 0 else 0
    
    def reset_metrics(self):
        """Reset all metrics for new test"""
        self.metrics = LoadTestMetrics(
            total_requests=0,
            successful_requests=0,
            failed_requests=0,
            avg_response_time=0.0,
            min_response_time=float('inf'),
            max_response_time=0.0,
            p95_response_time=0.0,
            p99_response_time=0.0,
            requests_per_second=0.0,
            error_rate=0.0,
            errors=[]
        )
        self.response_times = []

class TelephonyLoadTests:
    """Load tests for telephony endpoints"""
    
    @pytest.mark.asyncio
    async def test_health_endpoint_load(self):
        """Test health endpoint under load"""
        async with LoadTestRunner() as runner:
            # Test parameters
            concurrent_users = 50
            requests_per_user = 20
            total_requests = concurrent_users * requests_per_user
            
            print(f"Testing health endpoint with {concurrent_users} concurrent users, {requests_per_user} requests each")
            
            async def user_session():
                """Simulate a user making multiple requests"""
                for _ in range(requests_per_user):
                    await runner.make_request("GET", "/health")
                    await asyncio.sleep(0.01)  # Small delay between requests
            
            start_time = time.time()
            
            # Run concurrent user sessions
            tasks = [user_session() for _ in range(concurrent_users)]
            await asyncio.gather(*tasks)
            
            duration = time.time() - start_time
            runner.calculate_metrics(duration)
            
            # Assertions
            assert runner.metrics.total_requests == total_requests
            assert runner.metrics.error_rate < 1.0  # Less than 1% error rate
            assert runner.metrics.avg_response_time < 0.1  # Average response time under 100ms
            assert runner.metrics.p95_response_time < 0.2  # 95th percentile under 200ms
            assert runner.metrics.requests_per_second > 100  # At least 100 RPS
            
            print(f"✅ Health endpoint load test passed:")
            print(f"   Total requests: {runner.metrics.total_requests}")
            print(f"   Success rate: {100 - runner.metrics.error_rate:.2f}%")
            print(f"   Average response time: {runner.metrics.avg_response_time*1000:.2f}ms")
            print(f"   95th percentile: {runner.metrics.p95_response_time*1000:.2f}ms")
            print(f"   Requests per second: {runner.metrics.requests_per_second:.2f}")
    
    @pytest.mark.asyncio
    async def test_provider_list_load(self):
        """Test provider list endpoint under load"""
        async with LoadTestRunner() as runner:
            # Test parameters
            concurrent_users = 30
            requests_per_user = 10
            
            print(f"Testing provider list endpoint with {concurrent_users} concurrent users")
            
            async def user_session():
                for _ in range(requests_per_user):
                    await runner.make_request("GET", "/api/v1/providers")
                    await asyncio.sleep(0.05)
            
            start_time = time.time()
            tasks = [user_session() for _ in range(concurrent_users)]
            await asyncio.gather(*tasks)
            
            duration = time.time() - start_time
            runner.calculate_metrics(duration)
            
            # Assertions
            assert runner.metrics.error_rate < 2.0
            assert runner.metrics.avg_response_time < 0.5
            assert runner.metrics.p95_response_time < 1.0
            
            print(f"✅ Provider list load test passed:")
            print(f"   Success rate: {100 - runner.metrics.error_rate:.2f}%")
            print(f"   Average response time: {runner.metrics.avg_response_time*1000:.2f}ms")
    
    @pytest.mark.asyncio
    async def test_session_creation_load(self):
        """Test session creation endpoint under load"""
        async with LoadTestRunner() as runner:
            # Test parameters
            concurrent_users = 20
            requests_per_user = 5
            
            session_request = {
                "provider_type": "openai",
                "provider_model": "gpt-4",
                "strategy": "single_provider",
                "telephony_provider": "twilio"
            }
            
            print(f"Testing session creation with {concurrent_users} concurrent users")
            
            async def user_session():
                for i in range(requests_per_user):
                    await runner.make_request(
                        "POST", 
                        "/api/v1/sessions",
                        json=session_request
                    )
                    await asyncio.sleep(0.1)
            
            start_time = time.time()
            tasks = [user_session() for _ in range(concurrent_users)]
            await asyncio.gather(*tasks)
            
            duration = time.time() - start_time
            runner.calculate_metrics(duration)
            
            # Assertions
            assert runner.metrics.error_rate < 5.0  # Allow higher error rate for session creation
            assert runner.metrics.avg_response_time < 2.0  # Session creation can be slower
            assert runner.metrics.p95_response_time < 3.0
            
            print(f"✅ Session creation load test passed:")
            print(f"   Success rate: {100 - runner.metrics.error_rate:.2f}%")
            print(f"   Average response time: {runner.metrics.avg_response_time*1000:.2f}ms")
    
    @pytest.mark.asyncio
    async def test_compliance_api_load(self):
        """Test compliance API endpoints under load"""
        async with LoadTestRunner() as runner:
            # Test parameters
            concurrent_users = 25
            requests_per_user = 8
            
            print(f"Testing compliance API with {concurrent_users} concurrent users")
            
            async def user_session():
                for i in range(requests_per_user):
                    # Test different compliance endpoints
                    endpoints = [
                        "/api/compliance/regions",
                        "/api/compliance/consent-types",
                        f"/api/compliance/consents/test_user_{i}"
                    ]
                    
                    for endpoint in endpoints:
                        await runner.make_request("GET", endpoint)
                        await asyncio.sleep(0.02)
            
            start_time = time.time()
            tasks = [user_session() for _ in range(concurrent_users)]
            await asyncio.gather(*tasks)
            
            duration = time.time() - start_time
            runner.calculate_metrics(duration)
            
            # Assertions
            assert runner.metrics.error_rate < 3.0
            assert runner.metrics.avg_response_time < 0.3
            assert runner.metrics.p95_response_time < 0.5
            
            print(f"✅ Compliance API load test passed:")
            print(f"   Success rate: {100 - runner.metrics.error_rate:.2f}%")
            print(f"   Average response time: {runner.metrics.avg_response_time*1000:.2f}ms")
    
    @pytest.mark.asyncio
    async def test_alerting_api_load(self):
        """Test alerting API endpoints under load"""
        async with LoadTestRunner() as runner:
            # Test parameters
            concurrent_users = 15
            requests_per_user = 10
            
            print(f"Testing alerting API with {concurrent_users} concurrent users")
            
            async def user_session():
                for i in range(requests_per_user):
                    # Test metric submission
                    metric_data = {
                        "metric_type": "call_quality",
                        "value": 4.5,
                        "labels": {"provider": "twilio", "region": "us-east"}
                    }
                    
                    await runner.make_request(
                        "POST",
                        "/api/alerting/metrics",
                        json=metric_data
                    )
                    
                    # Test alerts retrieval
                    await runner.make_request("GET", "/api/alerting/alerts")
                    
                    await asyncio.sleep(0.05)
            
            start_time = time.time()
            tasks = [user_session() for _ in range(concurrent_users)]
            await asyncio.gather(*tasks)
            
            duration = time.time() - start_time
            runner.calculate_metrics(duration)
            
            # Assertions
            assert runner.metrics.error_rate < 3.0
            assert runner.metrics.avg_response_time < 0.4
            assert runner.metrics.p95_response_time < 0.8
            
            print(f"✅ Alerting API load test passed:")
            print(f"   Success rate: {100 - runner.metrics.error_rate:.2f}%")
            print(f"   Average response time: {runner.metrics.avg_response_time*1000:.2f}ms")

class StressTestScenarios:
    """Stress testing scenarios for extreme load conditions"""
    
    @pytest.mark.asyncio
    async def test_sustained_load(self):
        """Test system under sustained load over time"""
        async with LoadTestRunner() as runner:
            duration_seconds = 60  # 1 minute sustained test
            target_rps = 50  # Target requests per second
            concurrent_users = 25
            
            print(f"Running sustained load test for {duration_seconds} seconds at {target_rps} RPS")
            
            async def sustained_requests():
                """Generate sustained requests"""
                end_time = time.time() + duration_seconds
                
                while time.time() < end_time:
                    await runner.make_request("GET", "/health")
                    await asyncio.sleep(1.0 / target_rps)
            
            start_time = time.time()
            tasks = [sustained_requests() for _ in range(concurrent_users)]
            await asyncio.gather(*tasks)
            
            actual_duration = time.time() - start_time
            runner.calculate_metrics(actual_duration)
            
            # Assertions for sustained load
            assert runner.metrics.error_rate < 2.0
            assert runner.metrics.requests_per_second >= target_rps * 0.8  # At least 80% of target RPS
            assert runner.metrics.avg_response_time < 0.2
            
            print(f"✅ Sustained load test passed:")
            print(f"   Duration: {actual_duration:.2f}s")
            print(f"   Requests per second: {runner.metrics.requests_per_second:.2f}")
            print(f"   Success rate: {100 - runner.metrics.error_rate:.2f}%")
    
    @pytest.mark.asyncio
    async def test_burst_load(self):
        """Test system under burst load conditions"""
        async with LoadTestRunner() as runner:
            # Burst parameters
            burst_size = 100  # 100 concurrent requests
            burst_count = 5   # 5 bursts
            burst_interval = 2  # 2 seconds between bursts
            
            print(f"Running burst load test: {burst_size} requests x {burst_count} bursts")
            
            for burst_num in range(burst_count):
                print(f"  Executing burst {burst_num + 1}/{burst_count}")
                
                # Create burst of requests
                tasks = [
                    runner.make_request("GET", "/health")
                    for _ in range(burst_size)
                ]
                
                await asyncio.gather(*tasks)
                
                if burst_num < burst_count - 1:
                    await asyncio.sleep(burst_interval)
            
            runner.calculate_metrics(burst_count * burst_interval)
            
            # Assertions for burst load
            assert runner.metrics.error_rate < 5.0  # Allow higher error rate during bursts
            assert runner.metrics.avg_response_time < 0.5
            
            print(f"✅ Burst load test passed:")
            print(f"   Total requests: {runner.metrics.total_requests}")
            print(f"   Success rate: {100 - runner.metrics.error_rate:.2f}%")
            print(f"   Average response time: {runner.metrics.avg_response_time*1000:.2f}ms")
    
    @pytest.mark.asyncio
    async def test_ramp_up_load(self):
        """Test system with gradually increasing load"""
        async with LoadTestRunner() as runner:
            max_users = 50
            ramp_up_time = 30  # seconds
            step_users = 5
            step_duration = ramp_up_time // (max_users // step_users)
            
            print(f"Running ramp-up test: 0 -> {max_users} users over {ramp_up_time}s")
            
            async def user_requests(user_id: int):
                """Generate requests for a single user"""
                for _ in range(10):  # 10 requests per user
                    await runner.make_request("GET", "/health")
                    await asyncio.sleep(0.1)
            
            start_time = time.time()
            current_users = 0
            tasks = []
            
            # Gradually add users
            while current_users < max_users:
                new_users = min(step_users, max_users - current_users)
                
                for i in range(new_users):
                    task = asyncio.create_task(user_requests(current_users + i))
                    tasks.append(task)
                
                current_users += new_users
                await asyncio.sleep(step_duration)
            
            # Wait for all tasks to complete
            await asyncio.gather(*tasks)
            
            duration = time.time() - start_time
            runner.calculate_metrics(duration)
            
            # Assertions
            assert runner.metrics.error_rate < 3.0
            assert runner.metrics.avg_response_time < 0.3
            
            print(f"✅ Ramp-up load test passed:")
            print(f"   Peak users: {current_users}")
            print(f"   Total requests: {runner.metrics.total_requests}")
            print(f"   Success rate: {100 - runner.metrics.error_rate:.2f}%")

class PerformanceRegressionTests:
    """Performance regression tests to ensure no degradation"""
    
    @pytest.mark.asyncio
    async def test_response_time_regression(self):
        """Ensure response times haven't regressed"""
        async with LoadTestRunner() as runner:
            # Baseline expectations (in milliseconds)
            baseline_health = 50
            baseline_providers = 200
            baseline_sessions = 1000
            
            # Test health endpoint
            for _ in range(20):
                await runner.make_request("GET", "/health")
            
            runner.calculate_metrics(1.0)
            health_avg_ms = runner.metrics.avg_response_time * 1000
            
            assert health_avg_ms < baseline_health, f"Health endpoint regression: {health_avg_ms:.2f}ms > {baseline_health}ms"
            
            runner.reset_metrics()
            
            # Test providers endpoint
            for _ in range(10):
                await runner.make_request("GET", "/api/v1/providers")
            
            runner.calculate_metrics(1.0)
            providers_avg_ms = runner.metrics.avg_response_time * 1000
            
            assert providers_avg_ms < baseline_providers, f"Providers endpoint regression: {providers_avg_ms:.2f}ms > {baseline_providers}ms"
            
            print(f"✅ Performance regression test passed:")
            print(f"   Health endpoint: {health_avg_ms:.2f}ms (baseline: {baseline_health}ms)")
            print(f"   Providers endpoint: {providers_avg_ms:.2f}ms (baseline: {baseline_providers}ms)")

# Test execution utilities
async def run_all_load_tests():
    """Run all load tests and generate report"""
    print("🚀 Starting Milestone 6 Load Testing")
    print("=" * 50)
    
    test_classes = [
        TelephonyLoadTests(),
        StressTestScenarios(),
        PerformanceRegressionTests()
    ]
    
    results = []
    
    for test_class in test_classes:
        print(f"\n📊 Running {test_class.__class__.__name__}")
        print("-" * 30)
        
        methods = [method for method in dir(test_class) if method.startswith('test_')]
        
        for method_name in methods:
            try:
                method = getattr(test_class, method_name)
                await method()
                results.append({"test": method_name, "status": "PASSED"})
            except Exception as e:
                results.append({"test": method_name, "status": "FAILED", "error": str(e)})
                print(f"❌ {method_name} failed: {e}")
    
    # Generate summary report
    print("\n" + "=" * 50)
    print("📋 LOAD TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for r in results if r["status"] == "PASSED")
    failed = sum(1 for r in results if r["status"] == "FAILED")
    
    print(f"Total Tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {passed/len(results)*100:.1f}%")
    
    if failed > 0:
        print("\n❌ Failed Tests:")
        for result in results:
            if result["status"] == "FAILED":
                print(f"   - {result['test']}: {result.get('error', 'Unknown error')}")
    
    # Save detailed report
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total": len(results),
            "passed": passed,
            "failed": failed,
            "success_rate": passed/len(results)*100
        },
        "results": results
    }
    
    with open("load_test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: load_test_report.json")
    
    return failed == 0

if __name__ == "__main__":
    # Run load tests
    success = asyncio.run(run_all_load_tests())
    exit(0 if success else 1)