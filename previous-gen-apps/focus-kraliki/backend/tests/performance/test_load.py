"""
Performance Load Testing
Tests API performance under load
"""

import pytest
import asyncio
import time
from httpx import AsyncClient
from statistics import mean, median, stdev
from typing import List


class PerformanceMetrics:
    """Track performance metrics for load testing."""

    def __init__(self):
        self.response_times: List[float] = []
        self.errors: List[str] = []
        self.successes = 0
        self.failures = 0

    def add_result(self, duration: float, success: bool, error: str = None):
        """Add a test result."""
        self.response_times.append(duration)
        if success:
            self.successes += 1
        else:
            self.failures += 1
            if error:
                self.errors.append(error)

    def get_summary(self) -> dict:
        """Get performance summary statistics."""
        if not self.response_times:
            return {
                "total_requests": 0,
                "successes": 0,
                "failures": 0,
                "error_rate": 0.0
            }

        return {
            "total_requests": len(self.response_times),
            "successes": self.successes,
            "failures": self.failures,
            "error_rate": self.failures / len(self.response_times) if self.response_times else 0,
            "response_times": {
                "mean_ms": mean(self.response_times) * 1000,
                "median_ms": median(self.response_times) * 1000,
                "min_ms": min(self.response_times) * 1000,
                "max_ms": max(self.response_times) * 1000,
                "stdev_ms": stdev(self.response_times) * 1000 if len(self.response_times) > 1 else 0
            },
            "performance_grade": self._calculate_grade()
        }

    def _calculate_grade(self) -> str:
        """Calculate performance grade based on metrics."""
        if not self.response_times:
            return "N/A"

        avg_time = mean(self.response_times) * 1000  # Convert to ms
        error_rate = self.failures / len(self.response_times) if self.response_times else 0

        if avg_time < 100 and error_rate < 0.01:
            return "A+ (Excellent)"
        elif avg_time < 200 and error_rate < 0.05:
            return "A (Good)"
        elif avg_time < 500 and error_rate < 0.1:
            return "B (Acceptable)"
        elif avg_time < 1000 and error_rate < 0.2:
            return "C (Needs Improvement)"
        else:
            return "D (Poor)"


class TestTaskEndpointsLoad:
    """Load testing for task endpoints."""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_task_list_concurrent_load(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test concurrent task list requests."""
        metrics = PerformanceMetrics()
        num_requests = 50

        async def make_request():
            start = time.time()
            try:
                response = await async_client.get("/tasks", headers=auth_headers)
                duration = time.time() - start
                metrics.add_result(duration, response.status_code == 200)
            except Exception as e:
                duration = time.time() - start
                metrics.add_result(duration, False, str(e))

        # Execute requests concurrently
        await asyncio.gather(*[make_request() for _ in range(num_requests)])

        summary = metrics.get_summary()
        print(f"\n=== Task List Load Test ===")
        print(f"Requests: {summary['total_requests']}")
        print(f"Success: {summary['successes']}, Failed: {summary['failures']}")
        print(f"Error Rate: {summary['error_rate']:.2%}")
        print(f"Avg Response: {summary['response_times']['mean_ms']:.2f}ms")
        print(f"Median: {summary['response_times']['median_ms']:.2f}ms")
        print(f"P95: {summary['response_times']['max_ms']:.2f}ms")
        print(f"Grade: {summary['performance_grade']}")

        # Assert performance requirements
        assert summary['error_rate'] < 0.05, "Error rate too high (>5%)"
        assert summary['response_times']['mean_ms'] < 1000, "Average response time too slow (>1s)"

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_task_create_throughput(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test task creation throughput."""
        metrics = PerformanceMetrics()
        num_requests = 20

        async def create_task(index: int):
            start = time.time()
            try:
                response = await async_client.post(
                    "/tasks",
                    json={
                        "title": f"Load Test Task {index}",
                        "priority": 3
                    },
                    headers=auth_headers
                )
                duration = time.time() - start
                metrics.add_result(duration, response.status_code in [200, 201])
            except Exception as e:
                duration = time.time() - start
                metrics.add_result(duration, False, str(e))

        start_time = time.time()
        await asyncio.gather(*[create_task(i) for i in range(num_requests)])
        total_time = time.time() - start_time

        summary = metrics.get_summary()
        throughput = num_requests / total_time

        print(f"\n=== Task Create Throughput Test ===")
        print(f"Total Time: {total_time:.2f}s")
        print(f"Throughput: {throughput:.2f} req/s")
        print(f"Avg Response: {summary['response_times']['mean_ms']:.2f}ms")
        print(f"Grade: {summary['performance_grade']}")

        # Assert throughput requirements
        assert throughput > 5, "Throughput too low (<5 req/s)"
        assert summary['error_rate'] < 0.1, "Error rate too high (>10%)"


class TestAuthEndpointsLoad:
    """Load testing for authentication endpoints."""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_token_verification_load(
        self,
        async_client: AsyncClient,
        auth_token: str
    ):
        """Test JWT token verification performance under load."""
        metrics = PerformanceMetrics()
        num_requests = 100

        async def verify_token():
            start = time.time()
            try:
                response = await async_client.get(
                    "/auth/me",
                    headers={"Authorization": f"Bearer {auth_token}"}
                )
                duration = time.time() - start
                metrics.add_result(duration, response.status_code == 200)
            except Exception as e:
                duration = time.time() - start
                metrics.add_result(duration, False, str(e))

        await asyncio.gather(*[verify_token() for _ in range(num_requests)])

        summary = metrics.get_summary()
        print(f"\n=== Token Verification Load Test ===")
        print(f"Requests: {summary['total_requests']}")
        print(f"Avg Response: {summary['response_times']['mean_ms']:.2f}ms")
        print(f"Median: {summary['response_times']['median_ms']:.2f}ms")
        print(f"Grade: {summary['performance_grade']}")

        # JWT verification should be very fast
        assert summary['response_times']['mean_ms'] < 200, "Token verification too slow"
        assert summary['error_rate'] == 0, "No errors expected for valid tokens"


class TestProjectEndpointsLoad:
    """Load testing for project endpoints."""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_project_list_load(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test project list endpoint under load."""
        metrics = PerformanceMetrics()
        num_requests = 30

        async def make_request():
            start = time.time()
            try:
                response = await async_client.get("/projects", headers=auth_headers)
                duration = time.time() - start
                metrics.add_result(duration, response.status_code == 200)
            except Exception as e:
                duration = time.time() - start
                metrics.add_result(duration, False, str(e))

        await asyncio.gather(*[make_request() for _ in range(num_requests)])

        summary = metrics.get_summary()
        print(f"\n=== Project List Load Test ===")
        print(f"Avg Response: {summary['response_times']['mean_ms']:.2f}ms")
        print(f"Error Rate: {summary['error_rate']:.2%}")
        print(f"Grade: {summary['performance_grade']}")

        assert summary['error_rate'] < 0.05
        assert summary['response_times']['mean_ms'] < 1000


class TestDatabaseQueryPerformance:
    """Test database query optimization."""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_task_filtering_performance(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user,
        db
    ):
        """Test performance of task filtering with many records."""
        from app.models.task import Task, TaskStatus
        from app.core.security_v2 import generate_id

        # Create 100 test tasks
        tasks = [
            Task(
                id=generate_id(),
                title=f"Task {i}",
                userId=test_user.id,
                status=TaskStatus.PENDING if i % 2 == 0 else TaskStatus.COMPLETED,
                priority=i % 5
            )
            for i in range(100)
        ]

        for task in tasks:
            db.add(task)
        db.commit()

        # Test filtering performance
        metrics = PerformanceMetrics()

        async def filter_tasks():
            start = time.time()
            try:
                response = await async_client.get(
                    "/tasks?status=PENDING&priority=3&limit=50",
                    headers=auth_headers
                )
                duration = time.time() - start
                metrics.add_result(duration, response.status_code == 200)
            except Exception as e:
                duration = time.time() - start
                metrics.add_result(duration, False, str(e))

        await asyncio.gather(*[filter_tasks() for _ in range(20)])

        summary = metrics.get_summary()
        print(f"\n=== Task Filtering Performance (100 records) ===")
        print(f"Avg Response: {summary['response_times']['mean_ms']:.2f}ms")
        print(f"Grade: {summary['performance_grade']}")

        # Filtering should remain fast even with many records
        assert summary['response_times']['mean_ms'] < 500


@pytest.mark.asyncio
@pytest.mark.slow
async def test_overall_api_health_under_load(
    async_client: AsyncClient,
    auth_headers: dict
):
    """Test overall API health under mixed load."""
    metrics = PerformanceMetrics()

    async def mixed_load():
        """Execute mixed requests."""
        endpoints = [
            ("/tasks", "GET"),
            ("/projects", "GET"),
            ("/auth/me", "GET"),
            ("/health", "GET")
        ]

        for endpoint, method in endpoints:
            start = time.time()
            try:
                if method == "GET":
                    response = await async_client.get(endpoint, headers=auth_headers)
                duration = time.time() - start
                metrics.add_result(duration, response.status_code in [200, 401])
            except Exception as e:
                duration = time.time() - start
                metrics.add_result(duration, False, str(e))

    await asyncio.gather(*[mixed_load() for _ in range(10)])

    summary = metrics.get_summary()
    print(f"\n=== Overall API Health Test ===")
    print(f"Total Requests: {summary['total_requests']}")
    print(f"Success Rate: {(summary['successes'] / summary['total_requests'] * 100):.1f}%")
    print(f"Avg Response: {summary['response_times']['mean_ms']:.2f}ms")
    print(f"Overall Grade: {summary['performance_grade']}")

    assert summary['error_rate'] < 0.1
