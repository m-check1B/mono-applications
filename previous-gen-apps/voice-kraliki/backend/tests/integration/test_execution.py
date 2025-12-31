#!/usr/bin/env python3
"""
Test script for the campaign execution engine.
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.campaigns.service import CampaignService
from app.campaigns.execution import ScriptExecutor, ExecutionContext


async def test_script_execution():
    """Test the script execution system."""
    print("🧪 Testing Script Execution System...")
    
    try:
        # Initialize campaign service
        campaign_service = CampaignService()
        
        # Get a working campaign
        campaign = campaign_service.get_campaign(1)  # English Insurance
        if not campaign:
            print("❌ Could not load campaign 1")
            return False
        
        print(f"✅ Loaded campaign: {campaign.title}")
        
        # Create script executor
        executor = ScriptExecutor(campaign)
        
        # Start execution
        context = executor.start_execution()
        print(f"✅ Started execution with session ID: {context.session_id}")
        print(f"✅ Current state: {context.state}")
        print(f"✅ Current step: {context.current_step}[{context.step_index}]")
        
        # Execute first step
        result = executor.execute_step(context)
        print(f"✅ First step execution result:")
        print(f"   Success: {result.success}")
        print(f"   Message: {result.message}")
        print(f"   Next step: {result.next_step}")
        print(f"   Data to collect: {result.data_to_collect}")
        
        # Update context state
        if result.data_to_collect:
            context.state = "waiting_for_response"
            print(f"✅ Waiting for response for variable: {result.data_to_collect.get('variable')}")
            
            # Simulate user response
            test_response = "2"
            print(f"✅ Simulating user response: {test_response}")
            
            # Process response
            result = executor.process_response(context, test_response)
            print(f"✅ Response processing result:")
            print(f"   Success: {result.success}")
            print(f"   Message: {result.message}")
            print(f"   Next step: {result.next_step}")
            print(f"   Collected data: {context.collected_data}")
            
            # Continue execution
            if result.success and not result.should_end_call:
                result = executor.execute_step(context)
                print(f"✅ Next step execution result:")
                print(f"   Success: {result.success}")
                print(f"   Message: {result.message}")
                print(f"   Next step: {result.next_step}")
        
        print(f"✅ Final state: {context.state}")
        print(f"✅ Final disposition: {context.disposition}")
        print(f"✅ Execution history length: {len(context.execution_history)}")
        
        print("✅ Script Execution System Test: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Script execution test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_script_execution())
    sys.exit(0 if success else 1)