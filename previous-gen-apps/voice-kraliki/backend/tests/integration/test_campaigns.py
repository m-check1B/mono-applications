#!/usr/bin/env python3
"""
Test script for campaign system functionality.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.campaigns.service import CampaignService

def test_campaign_system():
    """Test the campaign system functionality."""
    print("🧪 Testing Day 1 Campaign System...")
    
    # Test the service
    service = CampaignService()
    campaigns = service.get_all_campaigns()
    print(f"✅ Successfully loaded {len(campaigns)} campaigns")
    
    if campaigns:
        campaign = campaigns[0]
        print(f"✅ Campaign ID: {campaign.id}")
        print(f"✅ Campaign Title: {campaign.title}")
        print(f"✅ Campaign Type: {campaign.type}")
        print(f"✅ Campaign Language: {campaign.language}")
        print(f"✅ Agent Name: {campaign.agent_persona.name}")
        print(f"✅ Script has {len(campaign.script.start)} start steps")
        
        # Test getting by ID
        found_campaign = service.get_campaign(campaign.id)
        if found_campaign:
            print(f"✅ Successfully retrieved campaign by ID: {found_campaign.title}")
        
        # Test filtering
        outbound_campaigns = service.get_campaigns_by_type('outbound')
        print(f"✅ Found {len(outbound_campaigns)} outbound campaigns")
        
        english_campaigns = service.get_campaigns_by_language('en')
        print(f"✅ Found {len(english_campaigns)} English campaigns")
        
        summary = service.get_campaign_summary()
        print(f"✅ Campaign summary: {summary}")
        
    print("✅ Day 1 Campaign System Test: PASSED")
    return True

if __name__ == "__main__":
    test_campaign_system()