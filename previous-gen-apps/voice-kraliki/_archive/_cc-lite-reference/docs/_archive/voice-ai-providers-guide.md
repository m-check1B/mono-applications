# Voice AI Providers Configuration Guide

Voice by Kraliki now supports multiple voice AI solutions with automatic cost-based routing and fallback mechanisms. This guide explains how to configure and use each provider optimally.

## 🎯 Quick Start

### Recommended Setup
```bash
# Economy tier (cost-effective)
VOICE_SOLUTION=auto
VOICE_AI_COST_TIER=economy
VOICE_AI_PROVIDER_FALLBACK=true

# Provider API keys (configure at least one)
GEMINI_API_KEY=your_gemini_key       # Free tier available
OPENAI_API_KEY=your_openai_key       # Paid service
DEEPGRAM_API_KEY=your_deepgram_key   # Paid service
```

## 📊 Provider Comparison

### Cost Analysis (Per Minute)

| Provider | Economy | Standard | Premium | Notes |
|----------|---------|----------|---------|-------|
| **Gemini Flash 2.5** | $0.00 | $0.02 | $0.02 | Free tier experimental |
| **OpenAI Realtime** | $0.06 | $0.12 | $0.24 | Mini vs Full model |
| **Deepgram Pipeline** | $0.12 | $0.12 | $0.12 | STT+LLM+TTS combined |

### Feature Comparison

| Feature | Gemini | OpenAI | Deepgram |
|---------|--------|--------|----------|
| **Native Audio** | ✅ | ✅ | ❌ |
| **Real-time** | ✅ | ✅ | ⚡ Pipeline |
| **Latency** | 800ms | 500ms | 600ms |
| **Reliability** | 95% | 99% | 97% |
| **Languages** | 100+ | 50+ | 30+ |
| **Free Tier** | ✅ | ❌ | ❌ |

### Quality Comparison

| Aspect | Gemini Flash 2.5 | OpenAI Realtime | Deepgram Pipeline |
|--------|------------------|-----------------|-------------------|
| **Voice Quality** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Conversation Flow** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Interruption Handling** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Context Understanding** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Multilingual** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

## 🛠️ Configuration Options

### Auto Provider Selection
```bash
# Automatic provider selection based on cost tier
VOICE_SOLUTION=auto
VOICE_AI_COST_TIER=economy  # economy, standard, premium
```

**Economy tier priority:**
1. Gemini Flash 2.5 (free)
2. OpenAI Mini Realtime (cheaper)
3. Deepgram Pipeline (fallback)

**Standard tier priority:**
1. OpenAI Realtime (best performance)
2. Gemini Flash 2.5 (cost-effective)
3. Deepgram Pipeline (reliable)

**Premium tier priority:**
1. OpenAI Realtime Premium (highest quality)
2. Deepgram Pipeline (enterprise)
3. Gemini Flash 2.5 (backup)

### Manual Provider Selection

#### Gemini Flash 2.5 (Recommended for Cost)
```bash
VOICE_SOLUTION=gemini-multimodal
GEMINI_API_KEY=your_api_key
GEMINI_MODEL=gemini-2.5-flash-exp
GEMINI_DEFAULT_VOICE=Kore
VOICE_AI_COST_TIER=economy
```

**Pros:**
- ✅ Free tier available
- ✅ Latest multimodal capabilities
- ✅ Native audio processing
- ✅ Excellent multilingual support
- ✅ Fast inference

**Cons:**
- ⚠️ Experimental model (may have rate limits)
- ⚠️ Slightly higher latency than OpenAI
- ⚠️ Less proven in production

#### OpenAI Realtime (Recommended for Quality)
```bash
VOICE_SOLUTION=openai-realtime
OPENAI_API_KEY=your_api_key
OPENAI_REALTIME_MODEL=gpt-4o-mini-realtime-preview-2024-12-17
OPENAI_DEFAULT_VOICE=nova
VOICE_AI_COST_TIER=economy  # Uses cheaper mini model
```

**Models:**
- `gpt-4o-mini-realtime-preview-2024-12-17` - Cheaper variant (economy)
- `gpt-4o-realtime-preview-2024-10-01` - Standard model
- `gpt-4o-realtime-preview-2024-12-17` - Latest premium

**Pros:**
- ✅ Lowest latency (500ms)
- ✅ Best conversation flow
- ✅ Excellent interruption handling
- ✅ High reliability (99%)
- ✅ Production-ready

**Cons:**
- ❌ No free tier
- ❌ Higher cost than Gemini
- ❌ Fewer languages than Gemini

#### Deepgram Pipeline (Traditional STT→LLM→TTS)
```bash
VOICE_SOLUTION=deepgram-pipeline
DEEPGRAM_API_KEY=your_api_key
OPENROUTER_API_KEY=your_openrouter_key
DEEPGRAM_LLM_MODEL=gpt-4o-mini
DEEPGRAM_DEFAULT_VOICE=asteria-en
```

**Pros:**
- ✅ Modular architecture
- ✅ Proven reliability
- ✅ Enterprise-grade transcription
- ✅ Flexible LLM selection

**Cons:**
- ❌ Higher latency (pipeline processing)
- ❌ More complex configuration
- ❌ Higher combined costs

## 🔄 Fallback Configuration

### Automatic Fallback
```bash
VOICE_AI_PROVIDER_FALLBACK=true
```

**Fallback order:**
1. Primary provider fails → Switch to secondary
2. Secondary fails → Switch to tertiary
3. All fail → Error handling

**Fallback triggers:**
- API rate limits exceeded
- Authentication failures
- Network timeouts
- Provider service outages

### Manual Fallback Control
```javascript
// Switch providers programmatically
const voiceManager = getVoiceManager();
await voiceManager.switchToFallbackProvider();
```

## 📈 Monitoring & Metrics

### Provider Metrics
```javascript
const metrics = voiceManager.getProviderMetrics();
console.log({
  provider: metrics.provider,           // Current provider
  costTier: metrics.costTier,          // Cost tier
  costPerMinute: metrics.estimatedCostPerMinute,
  latency: metrics.latencyMs,          // Expected latency
  reliability: metrics.reliability      // Reliability score
});
```

### Cost Tracking
```javascript
// Track costs in real-time
voiceManager.on('call.ended', (data) => {
  const duration = data.summary.duration;
  const cost = (duration / 1000 / 60) * metrics.estimatedCostPerMinute;
  console.log(`Call cost: $${cost.toFixed(4)}`);
});
```

## 🚨 Production Recommendations

### For Startups/Cost-Conscious
```bash
VOICE_SOLUTION=auto
VOICE_AI_COST_TIER=economy
GEMINI_API_KEY=your_key  # Primary (free tier)
OPENAI_API_KEY=your_key  # Fallback
```

### For Enterprise/Quality-First
```bash
VOICE_SOLUTION=openai-realtime
VOICE_AI_COST_TIER=standard
OPENAI_API_KEY=your_key  # Primary
GEMINI_API_KEY=your_key  # Fallback
DEEPGRAM_API_KEY=your_key  # Secondary fallback
```

### For High-Volume/Cost-Optimized
```bash
VOICE_SOLUTION=gemini-multimodal
VOICE_AI_COST_TIER=economy
GEMINI_API_KEY=your_key  # Primary (free tier)
OPENAI_API_KEY=your_key  # Fallback for quality calls
```

## 🔧 Advanced Configuration

### Custom Model Selection
```bash
# Override default models
GEMINI_MODEL=gemini-2.5-flash-exp
OPENAI_REALTIME_MODEL=gpt-4o-mini-realtime-preview-2024-12-17
DEEPGRAM_LLM_MODEL=gpt-4o-mini

# Custom voices
GEMINI_DEFAULT_VOICE=Kore
OPENAI_DEFAULT_VOICE=nova
DEEPGRAM_DEFAULT_VOICE=asteria-en
```

### Provider-Specific Settings
```bash
# OpenAI specific
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=8192

# Gemini specific
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_OUTPUT_TOKENS=8192

# Deepgram specific
DEEPGRAM_LANGUAGE=en-US
DEEPGRAM_MODEL=nova-2
```

## 🧪 Testing Configuration

### Test Provider Selection
```bash
# Test auto-selection logic
npm run test:voice-providers

# Test fallback mechanisms
npm run test:voice-fallback

# Test cost calculations
npm run test:voice-costs
```

### Monitor in Development
```bash
# Enable debug logging
LOG_LEVEL=debug
VOICE_DEBUG=true

# Watch provider switches
tail -f logs/voice-system.log | grep "provider"
```

## 📞 Use Case Recommendations

### Customer Service (High Volume)
- **Primary:** Gemini Flash 2.5 (cost-effective)
- **Fallback:** OpenAI Mini Realtime
- **Tier:** Economy

### Sales Calls (Quality Important)
- **Primary:** OpenAI Realtime Standard
- **Fallback:** Gemini Flash 2.5
- **Tier:** Standard

### Healthcare (Regulatory)
- **Primary:** Deepgram Pipeline (enterprise)
- **Fallback:** OpenAI Realtime
- **Tier:** Premium

### Multilingual Support
- **Primary:** Gemini Flash 2.5 (100+ languages)
- **Fallback:** Deepgram Pipeline
- **Tier:** Standard

## 🔍 Troubleshooting

### Common Issues

**Provider initialization failed:**
```bash
# Check API keys
echo $GEMINI_API_KEY
echo $OPENAI_API_KEY

# Verify provider availability
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
```

**High latency:**
```bash
# Switch to lower latency provider
VOICE_SOLUTION=openai-realtime
VOICE_AI_COST_TIER=standard
```

**Rate limits exceeded:**
```bash
# Enable automatic fallback
VOICE_AI_PROVIDER_FALLBACK=true

# Upgrade to paid tier
VOICE_AI_COST_TIER=standard
```

**Cost too high:**
```bash
# Use economy tier
VOICE_AI_COST_TIER=economy
VOICE_SOLUTION=gemini-multimodal
```

## 📚 Additional Resources

- [OpenAI Realtime API Documentation](https://platform.openai.com/docs/guides/realtime)
- [Gemini Multimodal Guide](https://ai.google.dev/gemini-api/docs/audio)
- [Deepgram Voice Agent Docs](https://developers.deepgram.com/docs/voice-agent)
- [Cost Optimization Guide](./cost-optimization.md)
- [Performance Tuning Guide](./performance-tuning.md)

---

**Last Updated:** December 2024
**Version:** Voice by Kraliki v2.0
**Author:** Voice AI Integration Team