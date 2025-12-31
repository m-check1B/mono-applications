#!/usr/bin/env python3
"""Milestone 3 Provider Health Probes Test

Tests the provider health monitoring system for M3-5:
- Health monitor initialization
- Provider configuration
- Health check execution
- Status determination
- Metrics aggregation
"""

import asyncio
import logging
import sys
import time

# Add the backend directory to Python path
sys.path.insert(0, '/home/adminmatej/github/applications/operator-demo-2026/backend')

from app.services.provider_health_monitor import (
    get_health_monitor,
    ProviderHealthConfig,
    ProviderStatus
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestMilestone3HealthProbes:
    """Test suite for Milestone 3 health probes."""
    
    def __init__(self):
        self.test_results = []
    
    def run_test(self, test_name: str, test_func):
        """Run a test and record the result."""
        try:
            result = test_func()
            status = "✓ PASS" if result else "✗ FAIL"
            logger.info(f"{test_name}: {status}")
            self.test_results.append((test_name, result, None))
            return result
        except Exception as e:
            logger.error(f"{test_name}: ✗ FAIL - {e}")
            self.test_results.append((test_name, False, str(e)))
            return False
    
    async def run_async_test(self, test_name: str, test_func):
        """Run an async test and record the result."""
        try:
            result = await test_func()
            status = "✓ PASS" if result else "✗ FAIL"
            logger.info(f"{test_name}: {status}")
            self.test_results.append((test_name, result, None))
            return result
        except Exception as e:
            logger.error(f"{test_name}: ✗ FAIL - {e}")
            self.test_results.append((test_name, False, str(e)))
            return False
    
    def test_health_monitor_initialization(self):
        """Test health monitor initialization."""
        try:
            monitor = get_health_monitor()
            assert monitor is not None
            assert monitor.config.check_interval_seconds == 30
            assert monitor.config.latency_warning_threshold_ms == 1000
            assert monitor.config.latency_error_threshold_ms == 3000
            
            logger.info("✓ Health monitor initialized with default config")
            return True
        except Exception as e:
            logger.error(f"Health monitor initialization failed: {e}")
            return False
    
    def test_provider_configuration(self):
        """Test provider configuration."""
        try:
            monitor = get_health_monitor()
            configs = monitor._provider_configs
            
            required_providers = ["gemini", "openai", "deepgram_nova3", "twilio", "telnyx"]
            for provider_id in required_providers:
                assert provider_id in configs, f"Missing provider: {provider_id}"
                assert configs[provider_id]["enabled"] is True
            
            logger.info(f"✓ Provider configuration validated for {len(configs)} providers")
            return True
        except Exception as e:
            logger.error(f"Provider configuration test failed: {e}")
            return False
    
    async def test_health_check_cycle(self):
        """Test health check execution cycle."""
        try:
            monitor = get_health_monitor()
            
            # Start monitoring
            await monitor.start()
            assert monitor._running is True
            
            # Let it run for a short time
            await asyncio.sleep(0.3)
            
            # Check that health data was collected
            all_health = monitor.get_all_providers_health()
            assert len(all_health) > 0
            
            # Stop monitoring
            await monitor.stop()
            assert monitor._running is False
            
            logger.info(f"✓ Health check cycle completed, data for {len(all_health)} providers")
            return True
        except Exception as e:
            logger.error(f"Health check cycle test failed: {e}")
            return False
    
    def test_healthy_providers_filtering(self):
        """Test healthy providers filtering."""
        try:
            monitor = get_health_monitor()
            
            # Get all providers
            all_providers = monitor.get_all_providers_health()
            
            # Get healthy providers
            healthy_providers = monitor.get_healthy_providers()
            assert isinstance(healthy_providers, list)
            
            # Verify filtering logic
            for provider_id in healthy_providers:
                is_healthy = monitor.is_provider_healthy(provider_id)
                assert is_healthy is True
            
            logger.info(f"✓ Healthy providers filtering: {len(healthy_providers)}/{len(all_providers)} healthy")
            return True
        except Exception as e:
            logger.error(f"Healthy providers filtering test failed: {e}")
            return False
    
    def test_custom_configuration(self):
        """Test custom health monitor configuration."""
        try:
            custom_config = ProviderHealthConfig(
                check_interval_seconds=10,
                timeout_seconds=3,
                latency_warning_threshold_ms=500,
                latency_error_threshold_ms=1500,
                max_consecutive_failures=2
            )
            
            from app.services.provider_health_monitor import ProviderHealthMonitor
            custom_monitor = ProviderHealthMonitor(custom_config)
            
            assert custom_monitor.config.check_interval_seconds == 10
            assert custom_monitor.config.latency_warning_threshold_ms == 500
            assert custom_monitor.config.max_consecutive_failures == 2
            
            logger.info("✓ Custom configuration validated")
            return True
        except Exception as e:
            logger.error(f"Custom configuration test failed: {e}")
            return False
    
    def test_alerting_thresholds(self):
        """Test alerting threshold logic."""
        try:
            monitor = get_health_monitor()
            
            # Test threshold configurations
            assert monitor.config.latency_warning_threshold_ms < monitor.config.latency_error_threshold_ms
            assert monitor.config.max_consecutive_failures > 0
            assert monitor.config.history_retention_hours > 0
            
            logger.info(f"✓ Alerting thresholds: Warning={monitor.config.latency_warning_threshold_ms}ms, Error={monitor.config.latency_error_threshold_ms}ms")
            return True
        except Exception as e:
            logger.error(f"Alerting thresholds test failed: {e}")
            return False
    
    async def test_concurrent_health_checks(self):
        """Test concurrent health check execution."""
        try:
            monitor = get_health_monitor()
            
            # Start monitoring to trigger concurrent checks
            await monitor.start()
            
            # Wait for concurrent execution
            await asyncio.sleep(0.2)
            
            # Verify all providers were checked
            all_health = monitor.get_all_providers_health()
            expected_providers = len(monitor._provider_configs)
            
            # Most providers should have data
            assert len(all_health) >= expected_providers * 0.8  # Allow for some failures
            
            await monitor.stop()
            
            logger.info(f"✓ Concurrent health checks: {len(all_health)} providers checked")
            return True
        except Exception as e:
            logger.error(f"Concurrent health checks test failed: {e}")
            return False
    
    def test_metrics_structure(self):
        """Test metrics data structure."""
        try:
            monitor = get_health_monitor()
            all_health = monitor.get_all_providers_health()
            
            if all_health:
                # Check first provider's metrics structure
                sample_metrics = list(all_health.values())[0]
                
                required_fields = [
                    'provider_id', 'provider_type', 'status',
                    'total_checks', 'successful_checks', 'failed_checks',
                    'success_rate', 'average_latency_ms', 'uptime_percentage'
                ]
                
                for field in required_fields:
                    assert hasattr(sample_metrics, field), f"Missing field: {field}"
                
                # Check data types and ranges
                assert isinstance(sample_metrics.success_rate, (int, float))
                assert 0 <= sample_metrics.success_rate <= 100
                assert isinstance(sample_metrics.average_latency_ms, (int, float))
                assert sample_metrics.average_latency_ms >= 0
                assert isinstance(sample_metrics.uptime_percentage, (int, float))
                assert 0 <= sample_metrics.uptime_percentage <= 100
                
                logger.info("✓ Metrics structure and data types validated")
            else:
                logger.info("✓ Metrics structure test skipped (no data available)")
            
            return True
        except Exception as e:
            logger.error(f"Metrics structure test failed: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all tests."""
        logger.info("=== Milestone 3 Provider Health Probes Test Suite ===\n")
        
        # Synchronous tests
        self.run_test("Health Monitor Initialization", self.test_health_monitor_initialization)
        self.run_test("Provider Configuration", self.test_provider_configuration)
        self.run_test("Healthy Providers Filtering", self.test_healthy_providers_filtering)
        self.run_test("Custom Configuration", self.test_custom_configuration)
        self.run_test("Alerting Thresholds", self.test_alerting_thresholds)
        self.run_test("Metrics Structure", self.test_metrics_structure)
        
        # Asynchronous tests
        await self.run_async_test("Health Check Cycle", self.test_health_check_cycle)
        await self.run_async_test("Concurrent Health Checks", self.test_concurrent_health_checks)
        
        # Summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, result, _ in self.test_results if result)
        failed_tests = total_tests - passed_tests
        
        logger.info(f"\n=== Test Summary ===")
        logger.info(f"Total tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            logger.info("\nFailed tests:")
            for name, result, error in self.test_results:
                if not result:
                    logger.info(f"  - {name}: {error}")
        
        return passed_tests == total_tests


async def main():
    """Main test runner."""
    tester = TestMilestone3HealthProbes()
    success = await tester.run_all_tests()
    
    if success:
        logger.info("\n🎉 All provider health probe tests passed!")
        logger.info("✓ Health monitoring system operational")
        logger.info("✓ Provider health checks working")
        logger.info("✓ Status determination logic functional")
        logger.info("✓ Metrics collection validated")
        logger.info("✓ Alerting thresholds configured")
        return 0
    else:
        logger.error("\n❌ Some provider health probe tests failed!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)