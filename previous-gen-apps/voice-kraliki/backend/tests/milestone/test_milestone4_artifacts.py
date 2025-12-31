#!/usr/bin/env python3
"""
Milestone 4 Test: AI-First Experience & Automation - Call Artifacts

Tests post-call artifact APIs with persistence and search.
"""

import asyncio
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.call_artifacts import (
    CallArtifactsService,
    ArtifactType,
    CallStatus,
    SearchQuery,
    call_artifacts_service
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestCallArtifacts:
    """Test suite for Call Artifacts functionality"""
    
    def __init__(self):
        self.test_results = []
        self.test_call_ids = []
    
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        status = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"{status}: {test_name}")
        if details:
            logger.info(f"  Details: {details}")
        self.test_results.append((test_name, passed, details))
    
    async def test_call_record_creation(self):
        """Test creating call records"""
        logger.info("=== Testing Call Record Creation ===")
        
        try:
            # Create call record
            call_id = await call_artifacts_service.create_call_record(
                customer_phone="+1234567890",
                provider="gemini",
                agent_id="agent_001",
                metadata={"campaign": "insurance"}
            )
            
            self.test_call_ids.append(call_id)
            
            # Verify call record was created
            call_record = await call_artifacts_service.get_call_record(call_id)
            
            has_call_record = call_record is not None
            correct_phone = call_record.customer_phone == "+1234567890" if call_record else False
            correct_provider = call_record.provider == "gemini" if call_record else False
            correct_status = call_record.status == CallStatus.IN_PROGRESS if call_record else False
            
            passed = has_call_record and correct_phone and correct_provider and correct_status
            details = f"Call ID: {call_id}, Phone: {call_record.customer_phone if call_record else 'N/A'}"
            
            self.log_test("Call Record Creation", passed, details)
            
        except Exception as e:
            self.log_test("Call Record Creation", False, f"Error: {e}")
    
    async def test_artifact_creation(self):
        """Test adding artifacts to calls"""
        logger.info("=== Testing Artifact Creation ===")
        
        if not self.test_call_ids:
            self.log_test("Artifact Creation", False, "No test calls available")
            return
        
        try:
            call_id = self.test_call_ids[0]
            
            # Add different types of artifacts
            artifact_types = [
                (ArtifactType.SUMMARY, {"summary": "Customer called about insurance claim", "sentiment": "neutral"}),
                (ArtifactType.TRANSCRIPT, {"messages": [{"role": "user", "content": "Hello"}], "word_count": 150}),
                (ArtifactType.INSIGHTS, {"intent": "inquiry", "confidence": 0.8, "suggestions": []}),
                (ArtifactType.ANALYTICS, {"duration": 180, "silence_ratio": 0.1, "interruptions": 2})
            ]
            
            artifact_ids = []
            for artifact_type, content in artifact_types:
                artifact_id = await call_artifacts_service.add_artifact(
                    call_id=call_id,
                    artifact_type=artifact_type,
                    content=content,
                    metadata={"test": True}
                )
                artifact_ids.append(artifact_id)
            
            # Verify artifacts were created
            artifacts = await call_artifacts_service.get_call_artifacts(call_id)
            
            correct_count = len(artifacts) == len(artifact_types)
            has_all_types = all(
                any(a.artifact_type == at for a in artifacts) 
                for at, _ in artifact_types
            )
            
            passed = correct_count and has_all_types
            details = f"Artifacts: {len(artifacts)}, Types: {[a.artifact_type.value for a in artifacts]}"
            
            self.log_test("Artifact Creation", passed, details)
            
        except Exception as e:
            self.log_test("Artifact Creation", False, f"Error: {e}")
    
    async def test_call_status_updates(self):
        """Test updating call status"""
        logger.info("=== Testing Call Status Updates ===")
        
        if not self.test_call_ids:
            self.log_test("Call Status Updates", False, "No test calls available")
            return
        
        try:
            call_id = self.test_call_ids[0]
            
            # Update call status to completed
            success = await call_artifacts_service.update_call_status(
                call_id=call_id,
                status=CallStatus.COMPLETED,
                duration=300
            )
            
            # Verify status was updated
            call_record = await call_artifacts_service.get_call_record(call_id)
            
            update_success = success
            correct_status = call_record.status == CallStatus.COMPLETED if call_record else False
            correct_duration = call_record.duration == 300 if call_record else False
            has_end_time = call_record.ended_at is not None if call_record else False
            
            passed = update_success and correct_status and correct_duration and has_end_time
            details = f"Status: {call_record.status.value if call_record else 'N/A'}, Duration: {call_record.duration if call_record else 'N/A'}"
            
            self.log_test("Call Status Updates", passed, details)
            
        except Exception as e:
            self.log_test("Call Status Updates", False, f"Error: {e}")
    
    async def test_search_functionality(self):
        """Test search functionality for calls and artifacts"""
        logger.info("=== Testing Search Functionality ===")
        
        try:
            # Create additional test data
            call_id_2 = await call_artifacts_service.create_call_record(
                customer_phone="+0987654321",
                provider="openai",
                metadata={"campaign": "support"}
            )
            self.test_call_ids.append(call_id_2)
            
            # Add artifact with searchable content
            await call_artifacts_service.add_artifact(
                call_id=call_id_2,
                artifact_type=ArtifactType.TRANSCRIPT,
                content={"messages": [{"role": "user", "content": "I need help with my account"}]},
                metadata={"test": True}
            )
            
            # Update status
            await call_artifacts_service.update_call_status(call_id_2, CallStatus.COMPLETED, 120)
            
            # Test search calls
            search_query = SearchQuery(
                query="help account",
                filters={},
                limit=10
            )
            
            search_results = await call_artifacts_service.search_calls(search_query)
            
            # Test search artifacts
            artifact_search = await call_artifacts_service.search_artifacts(search_query)
            
            # Verify search results
            calls_found = search_results["total"] > 0
            artifacts_found = artifact_search["total"] > 0
            has_call_data = len(search_results["calls"]) > 0
            has_artifact_data = len(artifact_search["artifacts"]) > 0
            
            passed = calls_found and artifacts_found and has_call_data and has_artifact_data
            details = f"Calls: {search_results['total']}, Artifacts: {artifact_search['total']}"
            
            self.log_test("Search Functionality", passed, details)
            
        except Exception as e:
            self.log_test("Search Functionality", False, f"Error: {e}")
    
    async def test_analytics(self):
        """Test analytics functionality"""
        logger.info("=== Testing Analytics ===")
        
        try:
            # Get analytics for all time
            analytics = await call_artifacts_service.get_call_analytics()
            
            # Verify analytics structure
            has_period = "period" in analytics
            has_call_stats = "call_stats" in analytics
            has_provider_stats = "provider_stats" in analytics
            has_artifact_counts = "artifact_counts" in analytics
            
            # Verify call stats structure
            call_stats = analytics.get("call_stats", {})
            has_total = "total" in call_stats
            has_completion_rate = "completion_rate" in call_stats
            has_avg_duration = "average_duration" in call_stats
            
            passed = (has_period and has_call_stats and has_provider_stats and has_artifact_counts and
                     has_total and has_completion_rate and has_avg_duration)
            
            details = f"Total calls: {call_stats.get('total', 0)}, Completion rate: {call_stats.get('completion_rate', 0)}%"
            
            self.log_test("Analytics", passed, details)
            
        except Exception as e:
            self.log_test("Analytics", False, f"Error: {e}")
    
    async def test_filtering_and_pagination(self):
        """Test advanced filtering and pagination"""
        logger.info("=== Testing Filtering and Pagination ===")
        
        try:
            # Test filtering by status
            search_query = SearchQuery(
                query="",
                filters={"status": "completed"},
                limit=5,
                offset=0
            )
            
            filtered_results = await call_artifacts_service.search_calls(search_query)
            
            # Test filtering by provider
            provider_filter = SearchQuery(
                query="",
                filters={"provider": "gemini"},
                limit=5,
                offset=0
            )
            
            provider_results = await call_artifacts_service.search_calls(provider_filter)
            
            # Test pagination
            paginated_query = SearchQuery(
                query="",
                filters={},
                limit=1,
                offset=0
            )
            
            paginated_results = await call_artifacts_service.search_calls(paginated_query)
            
            # Verify results
            filtered_correct = all(call["status"] == "completed" for call in filtered_results["calls"])
            provider_correct = all(call["provider"] == "gemini" for call in provider_results["calls"])
            pagination_correct = len(paginated_results["calls"]) <= 1
            
            passed = filtered_correct and provider_correct and pagination_correct
            details = f"Filtered: {len(filtered_results['calls'])}, Provider: {len(provider_results['calls'])}, Paginated: {len(paginated_results['calls'])}"
            
            self.log_test("Filtering and Pagination", passed, details)
            
        except Exception as e:
            self.log_test("Filtering and Pagination", False, f"Error: {e}")
    
    async def test_artifact_retrieval(self):
        """Test artifact retrieval by type and ID"""
        logger.info("=== Testing Artifact Retrieval ===")
        
        if not self.test_call_ids:
            self.log_test("Artifact Retrieval", False, "No test calls available")
            return
        
        try:
            call_id = self.test_call_ids[0]
            
            # Get all artifacts
            all_artifacts = await call_artifacts_service.get_call_artifacts(call_id)
            
            # Get artifacts by type
            summary_artifacts = await call_artifacts_service.get_call_artifacts(
                call_id, [ArtifactType.SUMMARY]
            )
            
            # Get specific artifact
            if all_artifacts:
                artifact_id = all_artifacts[0].id
                specific_artifact = await call_artifacts_service.get_artifact(artifact_id)
                
                # Verify retrievals
                has_all = len(all_artifacts) > 0
                has_filtered = len(summary_artifacts) > 0
                has_specific = specific_artifact is not None
                correct_id = specific_artifact.id == artifact_id if specific_artifact else False
                
                passed = has_all and has_filtered and has_specific and correct_id
                details = f"All: {len(all_artifacts)}, Summary: {len(summary_artifacts)}, Specific: {specific_artifact.artifact_type.value if specific_artifact else 'N/A'}"
            else:
                passed = False
                details = "No artifacts found"
            
            self.log_test("Artifact Retrieval", passed, details)
            
        except Exception as e:
            self.log_test("Artifact Retrieval", False, f"Error: {e}")
    
    async def cleanup_test_data(self):
        """Clean up test data"""
        logger.info("=== Cleaning Up Test Data ===")
        
        try:
            for call_id in self.test_call_ids:
                await call_artifacts_service.delete_call_record(call_id)
            
            logger.info(f"Cleaned up {len(self.test_call_ids)} test calls")
            
        except Exception as e:
            logger.error(f"Error cleaning up test data: {e}")
    
    async def run_all_tests(self):
        """Run all test suites"""
        logger.info("=== Milestone 4 Call Artifacts Test Suite ===")
        
        await self.test_call_record_creation()
        await self.test_artifact_creation()
        await self.test_call_status_updates()
        await self.test_search_functionality()
        await self.test_analytics()
        await self.test_filtering_and_pagination()
        await self.test_artifact_retrieval()
        
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, passed, _ in self.test_results if passed)
        failed_tests = total_tests - passed_tests
        
        logger.info("\n=== Test Summary ===")
        logger.info(f"Total tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            logger.info("\nFailed Tests:")
            for test_name, passed, details in self.test_results:
                if not passed:
                    logger.info(f"  - {test_name}: {details}")
        
        # Cleanup
        await self.cleanup_test_data()
        
        return passed_tests == total_tests

async def main():
    """Main test runner"""
    tester = TestCallArtifacts()
    success = await tester.run_all_tests()
    
    if success:
        logger.info("\n🎉 All call artifacts tests passed!")
        logger.info("✓ Call record creation working")
        logger.info("✓ Artifact creation and management working")
        logger.info("✓ Call status updates working")
        logger.info("✓ Search functionality working")
        logger.info("✓ Analytics generation working")
        logger.info("✓ Filtering and pagination working")
        logger.info("✓ Artifact retrieval working")
    else:
        logger.info("\n❌ Some tests failed. Check the logs above.")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)