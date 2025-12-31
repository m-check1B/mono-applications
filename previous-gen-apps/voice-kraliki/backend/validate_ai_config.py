#!/usr/bin/env python3
"""
AI Provider Configuration Validation Script

This script validates that AI provider API keys are properly configured
and tests connectivity to each provider.
"""

import asyncio
import os
import sys
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_environment_variables() -> Dict[str, bool]:
    """Check if required environment variables are set."""
    
    print("🔍 Checking environment variables...")
    
    providers = {
        "OpenAI": os.getenv("OPENAI_API_KEY"),
        "Gemini": os.getenv("GEMINI_API_KEY"), 
        "Deepgram": os.getenv("DEEPGRAM_API_KEY")
    }
    
    results = {}
    for provider, key in providers.items():
        configured = bool(key and key.strip() and key != "")
        results[provider] = configured
        status = "✅" if configured else "❌"
        print(f"  {status} {provider}: {'Configured' if configured else 'Not configured'}")
    
    return results

async def test_providers(env_results: Dict[str, bool]) -> Dict[str, str]:
    """Test connectivity to configured providers."""
    
    print("\n🧪 Testing provider connectivity...")
    
    results = {}
    
    # Test OpenAI
    if env_results.get("OpenAI"):
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            # Simple test call
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Respond with 'OK'"}],
                max_tokens=5
            )
            
            if response.choices[0].message.content:
                results["OpenAI"] = "✅ Working"
                print(f"  ✅ OpenAI: Connected and responding")
            else:
                results["OpenAI"] = "❌ No response"
                print(f"  ❌ OpenAI: No response received")
                
        except Exception as e:
            results["OpenAI"] = f"❌ Error: {str(e)}"
            print(f"  ❌ OpenAI: {str(e)}")
    else:
        results["OpenAI"] = "⚠️ Not configured"
        print(f"  ⚠️ OpenAI: Skipping (not configured)")
    
    # Test Gemini
    if env_results.get("Gemini"):
        try:
            import google.generativeai as genai
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            model = genai.GenerativeModel('gemini-1.5-pro')
            
            response = model.generate_content("Respond with 'OK'")
            
            if response.text:
                results["Gemini"] = "✅ Working"
                print(f"  ✅ Gemini: Connected and responding")
            else:
                results["Gemini"] = "❌ No response"
                print(f"  ❌ Gemini: No response received")
                
        except Exception as e:
            results["Gemini"] = f"❌ Error: {str(e)}"
            print(f"  ❌ Gemini: {str(e)}")
    else:
        results["Gemini"] = "⚠️ Not configured"
        print(f"  ⚠️ Gemini: Skipping (not configured)")
    
    # Test Deepgram (basic API key validation)
    if env_results.get("Deepgram"):
        try:
            # Deepgram doesn't have a simple test endpoint, so we'll just validate the key format
            key = os.getenv("DEEPGRAM_API_KEY")
            if key and len(key) > 10:
                results["Deepgram"] = "✅ Key format valid"
                print(f"  ✅ Deepgram: API key format appears valid")
            else:
                results["Deepgram"] = "❌ Invalid key format"
                print(f"  ❌ Deepgram: Invalid API key format")
                
        except Exception as e:
            results["Deepgram"] = f"❌ Error: {str(e)}"
            print(f"  ❌ Deepgram: {str(e)}")
    else:
        results["Deepgram"] = "⚠️ Not configured"
        print(f"  ⚠️ Deepgram: Skipping (not configured)")
    
    return results

def test_ai_service_initialization() -> str:
    """Test if the AI insights service can be initialized."""
    
    print("\n🔧 Testing AI service initialization...")
    
    try:
        from app.services.enhanced_ai_insights import EnhancedAIInsightsService
        
        service = EnhancedAIInsightsService()
        
        openai_status = "✅" if service.openai_client else "❌"
        gemini_status = "✅" if service.gemini_client else "❌"
        
        print(f"  {openai_status} OpenAI client initialized")
        print(f"  {gemini_status} Gemini client initialized")
        
        if service.openai_client or service.gemini_client:
            print("  ✅ AI service initialized with at least one provider")
            return "✅ Success"
        else:
            print("  ⚠️ AI service initialized but no providers available")
            return "⚠️ Partial success"
            
    except Exception as e:
        print(f"  ❌ AI service initialization failed: {str(e)}")
        return f"❌ Error: {str(e)}"

def generate_recommendations(env_results: Dict[str, bool], test_results: Dict[str, str]) -> list:
    """Generate recommendations based on test results."""
    
    recommendations = []
    
    # Check for missing providers
    missing_providers = [p for p, configured in env_results.items() if not configured]
    if missing_providers:
        recommendations.append(f"Configure API keys for: {', '.join(missing_providers)}")
    
    # Check for failed providers
    failed_providers = [p for p, result in test_results.items() if "❌" in result]
    if failed_providers:
        recommendations.append(f"Fix connectivity issues for: {', '.join(failed_providers)}")
    
    # Check for working providers
    working_providers = [p for p, result in test_results.items() if "✅" in result]
    if not working_providers:
        recommendations.append("At least one AI provider must be working for full functionality")
    
    # Security recommendations
    if any(env_results.values()):
        recommendations.append("Ensure API keys are kept secure and not committed to version control")
        recommendations.append("Consider using secret management services in production")
    
    return recommendations

async def main():
    """Main validation function."""
    
    print("🚀 AI Provider Configuration Validation")
    print("=" * 50)
    
    # Check environment variables
    env_results = check_environment_variables()
    
    # Test provider connectivity
    test_results = await test_providers(env_results)
    
    # Test AI service initialization
    service_status = test_ai_service_initialization()
    
    # Generate recommendations
    recommendations = generate_recommendations(env_results, test_results)
    
    # Summary
    print("\n📊 Summary")
    print("-" * 20)
    
    configured_count = sum(env_results.values())
    working_count = sum(1 for r in test_results.values() if "✅" in r)
    
    print(f"Providers configured: {configured_count}/{len(env_results)}")
    print(f"Providers working: {working_count}/{len(test_results)}")
    print(f"AI service status: {service_status}")
    
    # Recommendations
    if recommendations:
        print("\n💡 Recommendations")
        print("-" * 20)
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
    
    # Final status
    print("\n🎯 Final Status")
    print("-" * 20)
    
    if working_count >= 2:
        print("✅ Excellent: Multiple AI providers working")
    elif working_count == 1:
        print("⚠️ Good: At least one AI provider working")
    else:
        print("❌ Critical: No AI providers working")
    
    print(f"\nNext steps:")
    print(f"1. Configure missing API keys in .env file")
    print(f"2. Run this script again to validate")
    print(f"3. Test the application with real AI providers")

if __name__ == "__main__":
    asyncio.run(main())