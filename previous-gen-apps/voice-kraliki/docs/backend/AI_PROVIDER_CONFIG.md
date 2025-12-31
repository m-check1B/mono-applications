# AI Provider Configuration Guide

## Overview
The operator-demo-2026 application supports multiple AI providers for different capabilities:

### Supported Providers
1. **OpenAI** - GPT models for advanced intent classification and sentiment analysis
2. **Google Gemini** - Conversation summarization and suggestions  
3. **Deepgram** - Speech-to-text and text-to-speech services

## Configuration Steps

### 1. Obtain API Keys

#### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy the key (starts with `sk-`)

#### Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key

#### Deepgram API Key
1. Go to [Deepgram Console](https://console.deepgram.com/)
2. Sign up and create an API key
3. Copy the key

### 2. Configure Environment Variables

Update your `.env` file with the API keys:

```bash
# AI Provider API Keys
OPENAI_API_KEY="sk-your-openai-api-key-here"
GEMINI_API_KEY="your-gemini-api-key-here"  
DEEPGRAM_API_KEY="your-deepgram-api-key-here"
```

### 3. Provider Capabilities

#### OpenAI
- **Models**: GPT-4, GPT-3.5-turbo
- **Features**: Intent classification, sentiment analysis, agent suggestions
- **Usage**: Real-time conversation insights

#### Google Gemini  
- **Models**: Gemini-1.5-pro
- **Features**: Conversation summarization, contextual recommendations
- **Usage**: Post-call analysis and suggestions

#### Deepgram
- **Models**: Nova-3, Whisper
- **Features**: Speech-to-text, text-to-speech
- **Usage**: Real-time transcription and voice synthesis

### 4. Testing Configuration

After setting the API keys, test the configuration:

```bash
# Test AI insights service
python3 -c "
import os
from app.services.enhanced_ai_insights import EnhancedAIInsightsService

print('OpenAI Key configured:', bool(os.getenv('OPENAI_API_KEY')))
print('Gemini Key configured:', bool(os.getenv('GEMINI_API_KEY')))
print('Deepgram Key configured:', bool(os.getenv('DEEPGRAM_API_KEY')))

service = EnhancedAIInsightsService()
print('OpenAI client initialized:', service.openai_client is not None)
print('Gemini client initialized:', service.gemini_client is not None)
"
```

### 5. Production Considerations

#### Security
- Never commit API keys to version control
- Use environment variable management in production
- Consider using secret management services (AWS Secrets Manager, etc.)

#### Rate Limits
- Monitor API usage to avoid rate limits
- Implement caching where appropriate
- Consider multiple API keys for high-volume scenarios

#### Cost Management
- Set up usage alerts in provider dashboards
- Monitor token usage and costs
- Implement usage limits per user/session

### 6. Fallback Configuration

The application supports graceful degradation when providers are unavailable:

1. **Missing OpenAI**: Uses rule-based intent classification
2. **Missing Gemini**: Uses template-based suggestions  
3. **Missing Deepgram**: Falls back to other TTS/STT providers

### 7. Environment-Specific Configuration

#### Development
```bash
# Use test/limited API keys
OPENAI_API_KEY="sk-test-..."
GEMINI_API_KEY="test-key"
DEEPGRAM_API_KEY="test-key"
```

#### Production
```bash
# Use full production API keys
OPENAI_API_KEY="sk-proj-..."
GEMINI_API_KEY="AIzaSy..."
DEEPGRAM_API_KEY="..."
```

## Troubleshooting

### Common Issues

1. **Invalid API Key**
   - Verify key is copied correctly
   - Check key has required permissions
   - Ensure key is active and not expired

2. **Rate Limiting**
   - Monitor usage in provider dashboard
   - Implement exponential backoff
   - Consider upgrading plan

3. **Network Issues**
   - Check firewall settings
   - Verify API endpoints are accessible
   - Consider using API gateway in production

### Validation Script

Run this script to validate your configuration:

```python
import asyncio
import os
from app.services.enhanced_ai_insights import EnhancedAIInsightsService

async def validate_ai_providers():
    service = EnhancedAIInsightsService()
    
    # Test OpenAI
    if service.openai_client:
        try:
            response = await service.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            print("✅ OpenAI: Working")
        except Exception as e:
            print(f"❌ OpenAI: {e}")
    else:
        print("⚠️  OpenAI: Not configured")
    
    # Test Gemini
    if service.gemini_client:
        try:
            response = service.gemini_client.generate_content("Hello")
            print("✅ Gemini: Working")
        except Exception as e:
            print(f"❌ Gemini: {e}")
    else:
        print("⚠️  Gemini: Not configured")

if __name__ == "__main__":
    asyncio.run(validate_ai_providers())
```

## Next Steps

1. Configure your API keys in the `.env` file
2. Run the validation script to test connectivity
3. Test the application with real AI providers
4. Monitor usage and costs in provider dashboards