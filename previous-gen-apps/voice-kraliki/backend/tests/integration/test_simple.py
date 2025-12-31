#!/usr/bin/env python3

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.campaigns.simple_service import SimpleCampaignService

def test_simple_campaign_system():
    """Test the simplified campaign system"""
    print("🧪 Testing Simple Campaign System")
    print("=" * 50)
    
    # Initialize service
    service = SimpleCampaignService()
    
    # Test 1: Load campaigns
    print("\n📋 Test 1: Loading Campaigns")
    campaigns = service.get_all_campaigns()
    print(f"✅ Found {len(campaigns)} campaigns")
    
    for campaign in campaigns:
        print(f"  - {campaign.name} (ID: {campaign.id}, Lang: {campaign.language})")
        print(f"    Steps: {len(campaign.steps)}")
    
    # Test 2: Start English campaign
    print("\n🚀 Test 2: Starting English Campaign")
    english_campaign = service.get_campaign_by_id(1)
    if english_campaign:
        print(f"✅ Found English campaign: {english_campaign.name}")
        
        execution = service.start_execution(1)
        if execution:
            print(f"✅ Started execution with session: {execution.session_id}")
            print(f"   Step {execution.step_number}/{execution.total_steps}: {execution.current_step.text}")
            
            # Test 3: Process responses
            print("\n💬 Test 3: Processing Responses")
            session_id = execution.session_id
            
            # Simulate responses
            responses = [
                "Yes I have auto insurance",
                "I have 2 vehicles",
                "Yes I'm interested",
                "Yes that's okay"
            ]
            
            for i, response in enumerate(responses, 1):
                print(f"\n  Response {i}: {response}")
                next_step = service.process_response(session_id, response)
                if next_step:
                    print(f"  ✅ Step {next_step.step_number}/{next_step.total_steps}: {next_step.current_step.text}")
                    if next_step.is_complete:
                        print("  🎉 Campaign completed!")
                        break
                else:
                    print("  ❌ Failed to process response")
                    break
        else:
            print("❌ Failed to start execution")
    else:
        print("❌ English campaign not found")
    
    # Test 4: Start Czech campaign
    print("\n🇨🇿 Test 4: Starting Czech Campaign")
    czech_campaign = service.get_campaign_by_id(2)
    if czech_campaign:
        print(f"✅ Found Czech campaign: {czech_campaign.name}")
        
        execution = service.start_execution(2)
        if execution:
            print(f"✅ Started execution with session: {execution.session_id}")
            print(f"   Step {execution.step_number}/{execution.total_steps}: {execution.current_step.text}")
        else:
            print("❌ Failed to start execution")
    else:
        print("❌ Czech campaign not found")
    
    print("\n🎯 All tests completed!")

if __name__ == "__main__":
    test_simple_campaign_system()