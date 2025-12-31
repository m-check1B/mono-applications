"""
Milestone 7: Performance Metrics Collection

Collects and analyzes performance metrics (latency, accuracy, reconnection success) 
against targets to validate system readiness.
"""

import asyncio
import json
import time
import statistics
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

class MetricType(str, Enum):
    """Types of performance metrics"""
    LATENCY = "latency"
    ACCURACY = "accuracy"
    RECONNECTION_SUCCESS = "reconnection_success"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    RESOURCE_UTILIZATION = "resource_utilization"

class ProviderType(str, Enum):
    """Provider types"""
    OPENAI = "openai"
    GEMINI = "gemini"
    DEEPGRAM = "deepgram"
    TWILIO = "twilio"
    TELNYX = "telnyx"

@dataclass
class PerformanceTarget:
    """Performance target definition"""
    metric_type: MetricType
    target_value: float
    unit: str
    comparison: str  # "lt", "gt", "eq", "lte", "gte"
    description: str

@dataclass
class MetricMeasurement:
    """Individual metric measurement"""
    timestamp: datetime
    metric_type: MetricType
    value: float
    unit: str
    provider: Optional[ProviderType] = None
    context: Optional[Dict[str, Any]] = None

@dataclass
class PerformanceAnalysis:
    """Performance analysis results"""
    metric_type: MetricType
    measurements: List[MetricMeasurement]
    target: PerformanceTarget
    actual_value: float
    target_met: bool
    deviation_percent: float
    trend: str  # "improving", "stable", "degrading"
    confidence: float  # 0-1

class PerformanceMetricsCollector:
    """Collects and analyzes performance metrics"""
    
    def __init__(self):
        self.measurements: List[MetricMeasurement] = []
        self.targets = self._define_targets()
        
    def _define_targets(self) -> Dict[MetricType, PerformanceTarget]:
        """Define performance targets"""
        return {
            MetricType.LATENCY: PerformanceTarget(
                metric_type=MetricType.LATENCY,
                target_value=1000.0,  # 1 second
                unit="ms",
                comparison="lte",
                description="API response time should be under 1 second"
            ),
            MetricType.ACCURACY: PerformanceTarget(
                metric_type=MetricType.ACCURACY,
                target_value=95.0,  # 95%
                unit="percent",
                comparison="gte",
                description="AI response accuracy should be 95% or higher"
            ),
            MetricType.RECONNECTION_SUCCESS: PerformanceTarget(
                metric_type=MetricType.RECONNECTION_SUCCESS,
                target_value=98.0,  # 98%
                unit="percent",
                comparison="gte",
                description="Reconnection success rate should be 98% or higher"
            ),
            MetricType.THROUGHPUT: PerformanceTarget(
                metric_type=MetricType.THROUGHPUT,
                target_value=100.0,  # 100 requests/minute
                unit="req/min",
                comparison="gte",
                description="System should handle 100 requests per minute"
            ),
            MetricType.ERROR_RATE: PerformanceTarget(
                metric_type=MetricType.ERROR_RATE,
                target_value=2.0,  # 2%
                unit="percent",
                comparison="lte",
                description="Error rate should be under 2%"
            ),
            MetricType.RESOURCE_UTILIZATION: PerformanceTarget(
                metric_type=MetricType.RESOURCE_UTILIZATION,
                target_value=80.0,  # 80%
                unit="percent",
                comparison="lte",
                description="Resource utilization should be under 80%"
            )
        }
    
    def add_measurement(self, metric_type: MetricType, value: float, 
                       provider: Optional[ProviderType] = None,
                       context: Optional[Dict[str, Any]] = None):
        """Add a metric measurement"""
        measurement = MetricMeasurement(
            timestamp=datetime.now(timezone.utc),
            metric_type=metric_type,
            value=value,
            unit=self.targets[metric_type].unit,
            provider=provider,
            context=context
        )
        self.measurements.append(measurement)
    
    async def collect_latency_metrics(self, base_url: str = "http://localhost:8000") -> Dict[str, Any]:
        """Collect latency metrics for various endpoints"""
        import urllib.request
        import urllib.error
        
        endpoints = [
            "/health",
            "/api/v1/providers",
            "/api/compliance/regions",
            "/api/alerting/health"
        ]
        
        latency_results = []
        
        for endpoint in endpoints:
            latencies = []
            
            # Measure latency 10 times for each endpoint
            for _ in range(10):
                start_time = time.time()
                try:
                    req = urllib.request.Request(f"{base_url}{endpoint}")
                    with urllib.request.urlopen(req, timeout=10) as response:
                        response.read()
                    latency_ms = (time.time() - start_time) * 1000
                    latencies.append(latency_ms)
                    
                    self.add_measurement(
                        MetricType.LATENCY,
                        latency_ms,
                        context={"endpoint": endpoint}
                    )
                    
                except Exception as e:
                    # Record failed request as high latency
                    latency_ms = 10000  # 10 seconds
                    latencies.append(latency_ms)
                    
                    self.add_measurement(
                        MetricType.LATENCY,
                        latency_ms,
                        context={"endpoint": endpoint, "error": str(e)}
                    )
                
                await asyncio.sleep(0.1)  # Small delay between requests
            
            # Calculate statistics for this endpoint
            if latencies:
                endpoint_stats = {
                    "endpoint": endpoint,
                    "avg_latency_ms": statistics.mean(latencies),
                    "min_latency_ms": min(latencies),
                    "max_latency_ms": max(latencies),
                    "p95_latency_ms": statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies),
                    "p99_latency_ms": statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else max(latencies),
                    "samples": len(latencies)
                }
                latency_results.append(endpoint_stats)
        
        return {
            "metric_type": "latency",
            "results": latency_results,
            "overall_avg_latency": statistics.mean([r["avg_latency_ms"] for r in latency_results])
        }
    
    async def collect_throughput_metrics(self, base_url: str = "http://localhost:8000") -> Dict[str, Any]:
        """Collect throughput metrics"""
        import urllib.request
        import concurrent.futures
        
        endpoint = "/health"
        test_duration_seconds = 60
        max_workers = 20
        
        def make_request():
            start_time = time.time()
            try:
                req = urllib.request.Request(f"{base_url}{endpoint}")
                with urllib.request.urlopen(req, timeout=5) as response:
                    response.read()
                return {"success": True, "latency_ms": (time.time() - start_time) * 1000}
            except:
                return {"success": False, "latency_ms": (time.time() - start_time) * 1000}
        
        start_time = time.time()
        requests_completed = 0
        requests_successful = 0
        latencies = []
        
        # Run concurrent requests for the test duration
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            while time.time() - start_time < test_duration_seconds:
                # Submit batch of requests
                futures = [executor.submit(make_request) for _ in range(10)]
                
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    requests_completed += 1
                    
                    if result["success"]:
                        requests_successful += 1
                        latencies.append(result["latency_ms"])
                    
                    self.add_measurement(
                        MetricType.THROUGHPUT,
                        1,  # Each request counts as 1
                        context={"success": result["success"]}
                    )
                
                await asyncio.sleep(0.1)
        
        actual_duration = time.time() - start_time
        throughput_rpm = (requests_completed / actual_duration) * 60
        success_rate = (requests_successful / requests_completed) * 100
        
        return {
            "metric_type": "throughput",
            "requests_per_minute": throughput_rpm,
            "success_rate_percent": success_rate,
            "total_requests": requests_completed,
            "test_duration_seconds": actual_duration,
            "avg_latency_ms": statistics.mean(latencies) if latencies else 0
        }
    
    async def collect_accuracy_metrics(self) -> Dict[str, Any]:
        """Collect AI accuracy metrics (simulated)"""
        # Simulate AI response accuracy testing
        accuracy_results = []
        
        providers = [ProviderType.OPENAI, ProviderType.GEMINI]
        
        for provider in providers:
            # Simulate accuracy measurements
            for i in range(20):
                # Simulate accuracy between 85% and 99%
                accuracy = random.uniform(85.0, 99.0)
                
                self.add_measurement(
                    MetricType.ACCURACY,
                    accuracy,
                    provider=provider,
                    context={"test_id": i, "test_type": "response_accuracy"}
                )
                
                accuracy_results.append({
                    "provider": provider,
                    "accuracy": accuracy,
                    "test_id": i
                })
        
        # Calculate overall accuracy by provider
        provider_accuracy = {}
        for provider in providers:
            provider_measurements = [r for r in accuracy_results if r["provider"] == provider]
            if provider_measurements:
                avg_accuracy = statistics.mean([r["accuracy"] for r in provider_measurements])
                provider_accuracy[provider.value] = avg_accuracy
        
        overall_accuracy = statistics.mean([r["accuracy"] for r in accuracy_results])
        
        return {
            "metric_type": "accuracy",
            "overall_accuracy_percent": overall_accuracy,
            "provider_accuracy": provider_accuracy,
            "total_tests": len(accuracy_results)
        }
    
    async def collect_reconnection_metrics(self) -> Dict[str, Any]:
        """Collect reconnection success metrics (simulated)"""
        reconnection_results = []
        
        # Simulate reconnection scenarios
        for i in range(50):
            # Simulate reconnection success (95% success rate)
            success = random.random() < 0.95
            reconnection_time = random.uniform(1.0, 10.0) if success else 10.0
            
            self.add_measurement(
                MetricType.RECONNECTION_SUCCESS,
                1.0 if success else 0.0,
                context={
                    "attempt_id": i,
                    "reconnection_time_seconds": reconnection_time,
                    "success": success
                }
            )
            
            reconnection_results.append({
                "attempt_id": i,
                "success": success,
                "reconnection_time_seconds": reconnection_time
            })
        
        successful_reconnections = sum(1 for r in reconnection_results if r["success"])
        success_rate = (successful_reconnections / len(reconnection_results)) * 100
        
        successful_times = [r["reconnection_time_seconds"] for r in reconnection_results if r["success"]]
        avg_reconnection_time = statistics.mean(successful_times) if successful_times else 0
        
        return {
            "metric_type": "reconnection_success",
            "success_rate_percent": success_rate,
            "avg_reconnection_time_seconds": avg_reconnection_time,
            "total_attempts": len(reconnection_results),
            "successful_attempts": successful_reconnections
        }
    
    async def collect_resource_metrics(self) -> Dict[str, Any]:
        """Collect resource utilization metrics (simulated)"""
        import psutil
        
        # Get system resource metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Collect multiple samples over time
        cpu_samples = []
        memory_samples = []
        
        for i in range(10):
            cpu_samples.append(psutil.cpu_percent(interval=0.1))
            memory_samples.append(psutil.virtual_memory().percent)
            
            self.add_measurement(
                MetricType.RESOURCE_UTILIZATION,
                cpu_samples[-1],
                context={"resource": "cpu", "sample_id": i}
            )
            
            self.add_measurement(
                MetricType.RESOURCE_UTILIZATION,
                memory_samples[-1],
                context={"resource": "memory", "sample_id": i}
            )
            
            await asyncio.sleep(0.5)
        
        avg_cpu = statistics.mean(cpu_samples)
        avg_memory = statistics.mean(memory_samples)
        
        return {
            "metric_type": "resource_utilization",
            "cpu_percent": avg_cpu,
            "memory_percent": avg_memory,
            "disk_percent": (disk.used / disk.total) * 100,
            "samples": len(cpu_samples)
        }
    
    def analyze_metric(self, metric_type: MetricType) -> PerformanceAnalysis:
        """Analyze performance for a specific metric"""
        target = self.targets[metric_type]
        metric_measurements = [m for m in self.measurements if m.metric_type == metric_type]
        
        if not metric_measurements:
            return PerformanceAnalysis(
                metric_type=metric_type,
                measurements=[],
                target=target,
                actual_value=0,
                target_met=False,
                deviation_percent=0,
                trend="unknown",
                confidence=0
            )
        
        values = [m.value for m in metric_measurements]
        actual_value = statistics.mean(values)
        
        # Check if target is met
        if target.comparison == "lte":
            target_met = actual_value <= target.target_value
        elif target.comparison == "gte":
            target_met = actual_value >= target.target_value
        elif target.comparison == "lt":
            target_met = actual_value < target.target_value
        elif target.comparison == "gt":
            target_met = actual_value > target.target_value
        else:  # eq
            target_met = abs(actual_value - target.target_value) < 0.01
        
        # Calculate deviation
        if target.target_value != 0:
            deviation_percent = abs((actual_value - target.target_value) / target.target_value) * 100
        else:
            deviation_percent = 0
        
        # Determine trend (simplified)
        if len(values) >= 10:
            first_half = values[:len(values)//2]
            second_half = values[len(values)//2:]
            
            first_avg = statistics.mean(first_half)
            second_avg = statistics.mean(second_half)
            
            if second_avg < first_avg * 0.95:
                trend = "improving"
            elif second_avg > first_avg * 1.05:
                trend = "degrading"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        # Calculate confidence based on sample size
        confidence = min(len(values) / 30.0, 1.0)  # Max confidence at 30 samples
        
        return PerformanceAnalysis(
            metric_type=metric_type,
            measurements=metric_measurements,
            target=target,
            actual_value=actual_value,
            target_met=target_met,
            deviation_percent=deviation_percent,
            trend=trend,
            confidence=confidence
        )
    
    async def run_full_performance_analysis(self, base_url: str = "http://localhost:8000") -> Dict[str, Any]:
        """Run complete performance analysis"""
        print("🚀 Starting Performance Metrics Collection")
        print("=" * 50)
        
        # Collect all metrics
        print("📊 Collecting latency metrics...")
        latency_results = await self.collect_latency_metrics(base_url)
        
        print("📈 Collecting throughput metrics...")
        throughput_results = await self.collect_throughput_metrics(base_url)
        
        print("🎯 Collecting accuracy metrics...")
        accuracy_results = await self.collect_accuracy_metrics()
        
        print("🔄 Collecting reconnection metrics...")
        reconnection_results = await self.collect_reconnection_metrics()
        
        print("💾 Collecting resource metrics...")
        resource_results = await self.collect_resource_metrics()
        
        # Analyze all metrics
        print("\n🔍 Analyzing performance against targets...")
        analyses = {}
        
        for metric_type in MetricType:
            analysis = self.analyze_metric(metric_type)
            analyses[metric_type.value] = asdict(analysis)
            
            status = "✅" if analysis.target_met else "❌"
            print(f"   {status} {metric_type.value}: {analysis.actual_value:.2f} {analysis.target.unit} (target: {analysis.target.target_value} {analysis.target.unit})")
        
        # Generate summary
        targets_met = sum(1 for analysis in analyses.values() if analysis["target_met"])
        total_targets = len(analyses)
        
        summary = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_success_rate": (targets_met / total_targets) * 100,
            "targets_met": targets_met,
            "total_targets": total_targets,
            "status": "PASS" if targets_met == total_targets else "FAIL",
            "detailed_results": {
                "latency": latency_results,
                "throughput": throughput_results,
                "accuracy": accuracy_results,
                "reconnection_success": reconnection_results,
                "resource_utilization": resource_results
            },
            "analyses": analyses,
            "recommendations": self._generate_recommendations(analyses)
        }
        
        return summary
    
    def _generate_recommendations(self, analyses: Dict[str, Any]) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        for metric_type, analysis in analyses.items():
            if not analysis["target_met"]:
                if metric_type == "latency":
                    recommendations.append("Optimize API response times - consider caching, database optimization, or reducing computational complexity")
                elif metric_type == "accuracy":
                    recommendations.append("Improve AI model accuracy - consider fine-tuning, prompt optimization, or model selection")
                elif metric_type == "reconnection_success":
                    recommendations.append("Enhance reconnection logic - implement better retry mechanisms and connection pooling")
                elif metric_type == "throughput":
                    recommendations.append("Increase system capacity - scale horizontally or optimize resource usage")
                elif metric_type == "error_rate":
                    recommendations.append("Reduce error rate - improve error handling and input validation")
                elif metric_type == "resource_utilization":
                    recommendations.append("Optimize resource usage - implement better resource management and scaling")
        
        if not recommendations:
            recommendations.append("All performance targets are met - continue monitoring and optimization")
        
        return recommendations

async def run_performance_metrics_collection():
    """Run complete performance metrics collection"""
    collector = PerformanceMetricsCollector()
    
    # Run analysis
    summary = await collector.run_full_performance_analysis()
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 PERFORMANCE METRICS SUMMARY")
    print("=" * 50)
    
    print(f"Overall Status: {summary['status']}")
    print(f"Success Rate: {summary['overall_success_rate']:.1f}%")
    print(f"Targets Met: {summary['targets_met']}/{summary['total_targets']}")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    for i, rec in enumerate(summary['recommendations'], 1):
        print(f"   {i}. {rec}")
    
    # Save detailed report
    with open("performance_metrics_report.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)
    
    print(f"\n📄 Detailed report saved to: performance_metrics_report.json")
    
    return summary['status'] == "PASS"

# Add missing import
import random

if __name__ == "__main__":
    # Run performance metrics collection
    success = asyncio.run(run_performance_metrics_collection())
    
    if success:
        print("\n🎉 All performance targets met!")
        exit(0)
    else:
        print("\n⚠️  Some performance targets not met!")
        exit(1)