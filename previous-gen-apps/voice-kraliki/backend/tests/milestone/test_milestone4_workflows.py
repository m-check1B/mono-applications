#!/usr/bin/env python3
"""
Milestone 4 Test: AI-First Experience & Automation - Workflow Automation

Tests provider function-call events mapping to actionable workflows.
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.workflow_automation import (
    WorkflowAutomationService,
    FunctionCall,
    WorkflowStatus,
    WorkflowPriority,
    ActionType,
    workflow_automation_service
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestWorkflowAutomation:
    """Test suite for Workflow Automation functionality"""
    
    def __init__(self):
        self.test_results = []
    
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        status = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"{status}: {test_name}")
        if details:
            logger.info(f"  Details: {details}")
        self.test_results.append((test_name, passed, details))
    
    async def test_function_call_processing(self):
        """Test processing of function calls from providers"""
        logger.info("=== Testing Function Call Processing ===")
        
        test_cases = [
            {
                "function_name": "escalate_complaint",
                "provider": "gemini",
                "arguments": {"customer_id": "12345", "issue": "billing dispute"},
                "expected_workflows": 1
            },
            {
                "function_name": "schedule_followup",
                "provider": "openai",
                "arguments": {"customer_id": "67890", "product": "insurance"},
                "expected_workflows": 1
            },
            {
                "function_name": "unknown_function",
                "provider": "deepgram",
                "arguments": {"test": "data"},
                "expected_workflows": 0
            }
        ]
        
        for i, case in enumerate(test_cases):
            try:
                # Create function call
                function_call = FunctionCall(
                    id=f"test_call_{i}",
                    name=case["function_name"],
                    arguments=case["arguments"],
                    provider=case["provider"],
                    timestamp=datetime.now()
                )
                
                # Process function call
                result = await workflow_automation_service.process_function_call(function_call)
                
                # Check results
                workflows_executed = result.get("workflows_executed", 0)
                expected_workflows = case["expected_workflows"]
                
                passed = workflows_executed == expected_workflows
                details = f"Function: {case['function_name']}, Workflows: {workflows_executed}/{expected_workflows}"
                
                self.log_test(f"Function Call Processing Test {i+1}", passed, details)
                
            except Exception as e:
                self.log_test(f"Function Call Processing Test {i+1}", False, f"Error: {e}")
    
    async def test_workflow_execution(self):
        """Test workflow execution with multiple actions"""
        logger.info("=== Testing Workflow Execution ===")
        
        try:
            # Create a custom workflow
            from app.services.workflow_automation import Workflow, WorkflowAction
            
            actions = [
                WorkflowAction(
                    id="test_action_1",
                    type=ActionType.NOTIFICATION,
                    name="Test Notification",
                    description="Send test notification",
                    parameters={"recipient": "test@example.com", "message": "Test message"},
                    status=WorkflowStatus.PENDING
                ),
                WorkflowAction(
                    id="test_action_2",
                    type=ActionType.DATABASE_UPDATE,
                    name="Test Database Update",
                    description="Update test record",
                    parameters={"table": "test_table", "operation": "insert"},
                    status=WorkflowStatus.PENDING
                )
            ]
            
            workflow = Workflow(
                id="test_workflow",
                name="Test Workflow",
                description="Test workflow for automation",
                trigger_function="test_function",
                actions=actions,
                status=WorkflowStatus.PENDING,
                priority=WorkflowPriority.MEDIUM,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                metadata={"test": True}
            )
            
            # Register workflow
            workflow_automation_service.register_workflow(workflow)
            
            # Create function call to trigger workflow
            function_call = FunctionCall(
                id="trigger_call",
                name="test_function",
                arguments={"test": "data"},
                provider="test_provider",
                timestamp=datetime.now()
            )
            
            # Process function call
            result = await workflow_automation_service.process_function_call(function_call)
            
            # Check workflow execution
            workflows_executed = result.get("workflows_executed", 0)
            results = result.get("results", [])
            
            # Verify workflow was executed
            workflow_executed = workflows_executed > 0
            
            # Verify actions were completed
            actions_completed = False
            if results:
                workflow_result = results[0]
                actions_executed = workflow_result.get("actions_executed", 0)
                actions_completed = actions_executed == len(actions)
            
            passed = workflow_executed and actions_completed
            details = f"Workflows: {workflows_executed}, Actions completed: {actions_completed}"
            
            self.log_test("Workflow Execution", passed, details)
            
        except Exception as e:
            self.log_test("Workflow Execution", False, f"Error: {e}")
    
    async def test_action_handlers(self):
        """Test individual action handlers"""
        logger.info("=== Testing Action Handlers ===")
        
        action_types = [
            ActionType.API_CALL,
            ActionType.DATABASE_UPDATE,
            ActionType.NOTIFICATION,
            ActionType.APPROVAL_REQUEST,
            ActionType.ESCALATION,
            ActionType.CUSTOM
        ]
        
        for i, action_type in enumerate(action_types):
            try:
                # Create test context
                context = {
                    "function_call": {
                        "id": "test_call",
                        "name": "test_function",
                        "arguments": {"test": "data"},
                        "provider": "test_provider",
                        "timestamp": datetime.now().isoformat()
                    },
                    "action_parameters": {
                        "url": "https://api.example.com/test" if action_type == ActionType.API_CALL else None,
                        "table": "test_table" if action_type == ActionType.DATABASE_UPDATE else None,
                        "recipient": "test@example.com" if action_type == ActionType.NOTIFICATION else None,
                        "approver": "manager@example.com" if action_type == ActionType.APPROVAL_REQUEST else None,
                        "level": 1 if action_type == ActionType.ESCALATION else None,
                        "logic": {"custom": "action"} if action_type == ActionType.CUSTOM else None
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
                # Get handler
                handler = workflow_automation_service.action_handlers.get(action_type)
                if not handler:
                    self.log_test(f"Action Handler Test {i+1} ({action_type.value})", False, "No handler found")
                    continue
                
                # Execute action
                result = await handler(context)
                
                # Check result
                has_result = result is not None
                has_status = "status" in result
                has_type = result.get("type") == action_type.value
                
                passed = has_result and has_status and has_type
                details = f"Type: {action_type.value}, Status: {result.get('status', 'unknown')}"
                
                self.log_test(f"Action Handler Test {i+1} ({action_type.value})", passed, details)
                
            except Exception as e:
                self.log_test(f"Action Handler Test {i+1} ({action_type.value})", False, f"Error: {e}")
    
    async def test_workflow_templates(self):
        """Test predefined workflow templates"""
        logger.info("=== Testing Workflow Templates ===")
        
        template_functions = [
            "escalate_complaint",
            "schedule_followup",
            "create_support_ticket"
        ]
        
        for i, function_name in enumerate(template_functions):
            try:
                # Create function call
                function_call = FunctionCall(
                    id=f"template_test_{i}",
                    name=function_name,
                    arguments={"customer_id": f"test_{i}", "issue": "test issue"},
                    provider="test_provider",
                    timestamp=datetime.now()
                )
                
                # Process function call
                result = await workflow_automation_service.process_function_call(function_call)
                
                # Check that template workflow was triggered
                workflows_executed = result.get("workflows_executed", 0)
                has_workflow = workflows_executed > 0
                
                # Check workflow results
                has_results = False
                if has_workflow:
                    results = result.get("results", [])
                    if results:
                        workflow_result = results[0]
                        has_results = workflow_result.get("status") == "completed"
                
                passed = has_workflow and has_results
                details = f"Function: {function_name}, Workflows: {workflows_executed}, Completed: {has_results}"
                
                self.log_test(f"Workflow Template Test {i+1}", passed, details)
                
            except Exception as e:
                self.log_test(f"Workflow Template Test {i+1}", False, f"Error: {e}")
    
    async def test_execution_history(self):
        """Test execution history tracking"""
        logger.info("=== Testing Execution History ===")
        
        try:
            # Get initial history
            initial_history = workflow_automation_service.get_execution_history()
            initial_count = len(initial_history)
            
            # Create and process a function call
            function_call = FunctionCall(
                id="history_test",
                name="test_function",
                arguments={"test": "history"},
                provider="test_provider",
                timestamp=datetime.now()
            )
            
            await workflow_automation_service.process_function_call(function_call)
            
            # Get updated history
            updated_history = workflow_automation_service.get_execution_history()
            updated_count = len(updated_history)
            
            # Check that history was updated
            history_updated = updated_count > initial_count
            
            # Check history structure
            has_function_call_record = False
            for record in updated_history:
                if record.get("type") == "function_call_received":
                    func_call = record.get("function_call", {})
                    if func_call.get("id") == "history_test":
                        has_function_call_record = True
                        break
            
            passed = history_updated and has_function_call_record
            details = f"History: {initial_count} -> {updated_count}, Function call recorded: {has_function_call_record}"
            
            self.log_test("Execution History", passed, details)
            
        except Exception as e:
            self.log_test("Execution History", False, f"Error: {e}")
    
    async def test_workflow_status_tracking(self):
        """Test workflow status tracking"""
        logger.info("=== Testing Workflow Status Tracking ===")
        
        try:
            # Get a workflow from templates
            workflow_id = "complaint_escalation"
            workflow = workflow_automation_service.get_workflow_status(workflow_id)
            
            # Check initial status
            initial_status = workflow.status if workflow else None
            initial_is_pending = initial_status == WorkflowStatus.PENDING
            
            # Trigger the workflow
            function_call = FunctionCall(
                id="status_test",
                name="escalate_complaint",
                arguments={"customer_id": "status_test", "issue": "test complaint"},
                provider="test_provider",
                timestamp=datetime.now()
            )
            
            await workflow_automation_service.process_function_call(function_call)
            
            # Check updated status
            updated_workflow = workflow_automation_service.get_workflow_status(workflow_id)
            updated_status = updated_workflow.status if updated_workflow else None
            final_is_completed = updated_status == WorkflowStatus.COMPLETED
            
            passed = initial_is_pending and final_is_completed
            details = f"Status: {initial_status.value if initial_status else 'unknown'} -> {updated_status.value if updated_status else 'unknown'}"
            
            self.log_test("Workflow Status Tracking", passed, details)
            
        except Exception as e:
            self.log_test("Workflow Status Tracking", False, f"Error: {e}")
    
    async def run_all_tests(self):
        """Run all test suites"""
        logger.info("=== Milestone 4 Workflow Automation Test Suite ===")
        
        await self.test_function_call_processing()
        await self.test_workflow_execution()
        await self.test_action_handlers()
        await self.test_workflow_templates()
        await self.test_execution_history()
        await self.test_workflow_status_tracking()
        
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
        
        return passed_tests == total_tests

async def main():
    """Main test runner"""
    tester = TestWorkflowAutomation()
    success = await tester.run_all_tests()
    
    if success:
        logger.info("\n🎉 All workflow automation tests passed!")
        logger.info("✓ Function call processing working")
        logger.info("✓ Workflow execution with multiple actions working")
        logger.info("✓ Individual action handlers working")
        logger.info("✓ Predefined workflow templates working")
        logger.info("✓ Execution history tracking working")
        logger.info("✓ Workflow status tracking working")
    else:
        logger.info("\n❌ Some tests failed. Check the logs above.")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)