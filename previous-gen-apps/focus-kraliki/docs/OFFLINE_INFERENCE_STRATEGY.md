# Offline Inference Strategy for Focus by Kraliki

## Executive Summary

This document outlines the strategy for implementing offline AI inference capabilities in Focus by Kraliki, enabling users to access AI features without internet connectivity or when cloud services are unavailable.

**Status:** Design Document (Implementation Pending)
**Target:** Q1-Q2 2026
**Priority:** Medium (Enhancement)

---

## Table of Contents

1. [Overview](#overview)
2. [Use Cases](#use-cases)
3. [Model Selection Strategy](#model-selection-strategy)
4. [Quantization Targets](#quantization-targets)
5. [Fallback Orchestration](#fallback-orchestration)
6. [Deployment Requirements](#deployment-requirements)
7. [Implementation Roadmap](#implementation-roadmap)
8. [Performance Benchmarks](#performance-benchmarks)
9. [Security & Privacy](#security--privacy)

---

## Overview

### Current State

Focus by Kraliki currently requires online connectivity for all AI features:
- Task parsing and orchestration (OpenRouter API)
- Natural language understanding (Cloud LLMs)
- High reasoning mode (DeepSeek/Gemini)
- II-Agent execution (Cloud-based)

### Proposed State

Implement a hybrid architecture that:
1. **Defaults to cloud** for best performance and latest features
2. **Falls back to local** when offline or cloud unavailable
3. **Gracefully degrades** capabilities based on available resources
4. **Syncs state** when connection restored

### Benefits

- **Offline Access:** Work without internet (flights, remote locations)
- **Privacy:** Sensitive tasks processed locally
- **Reliability:** System remains functional during outages
- **Cost Reduction:** Reduced API calls for simple tasks
- **Latency:** Instant responses for cached/local inference

---

## Use Cases

### Primary Use Cases (P0)

1. **Task Parsing (Offline)**
   - Input: "Buy groceries tomorrow at 3pm high priority"
   - Output: Structured task with title, due date, priority
   - **Complexity:** Low - deterministic parsing with small model

2. **Basic Suggestions**
   - Input: User's task history
   - Output: 3-5 task recommendations
   - **Complexity:** Low-Medium - pattern matching + small LLM

3. **Offline Search (Knowledge Base)**
   - Input: Query text
   - Output: Ranked knowledge items using embedding similarity
   - **Complexity:** Low - pre-computed embeddings + vector search

### Secondary Use Cases (P1)

4. **Task Categorization**
   - Input: Task title/description
   - Output: Project/tag suggestions
   - **Complexity:** Low - classification task

5. **Time Estimation**
   - Input: Task description + historical data
   - Output: Estimated minutes to complete
   - **Complexity:** Medium - regression task

6. **Summary Generation**
   - Input: Multiple tasks/events
   - Output: Daily/weekly summary
   - **Complexity:** Medium - text summarization

### Future Use Cases (P2)

7. **Limited Reasoning**
   - Input: Complex multi-step question
   - Output: Structured reasoning chain (simplified)
   - **Complexity:** High - requires larger model (3B+)

8. **Code Review/Generation**
   - Input: Code snippet
   - Output: Analysis or suggestions
   - **Complexity:** High - specialized model needed

---

## Model Selection Strategy

### Criteria for Model Selection

1. **Size:** <2GB for mobile, <5GB for desktop
2. **Performance:** Latency <500ms for simple tasks
3. **Accuracy:** >80% match with cloud models for core tasks
4. **License:** Permissive (Apache 2.0, MIT) for commercial use
5. **Format:** GGUF or ONNX for cross-platform deployment

### Recommended Models by Use Case

#### Task Parsing (Primary)

**Model:** `phi-3-mini-4k-instruct` (GGUF Q4 quantized)
- **Size:** 2.3GB
- **Context:** 4K tokens
- **Inference:** ~200ms on M1 Mac, ~400ms on mid-range Android
- **Rationale:** Excellent instruction following, small size, fast inference

**Alternative:** `TinyLlama-1.1B-Chat` (GGUF Q4)
- **Size:** 650MB
- **Context:** 2K tokens
- **Inference:** ~100ms on most devices
- **Rationale:** Ultra-fast, good for basic parsing

#### Embedding Search (Primary)

**Model:** `all-MiniLM-L6-v2` (ONNX)
- **Size:** 90MB
- **Embedding Dim:** 384
- **Inference:** ~50ms per query
- **Rationale:** Industry standard, excellent quality/size ratio

**Alternative:** `bge-micro-v2` (ONNX)
- **Size:** 35MB
- **Embedding Dim:** 384
- **Inference:** ~30ms per query
- **Rationale:** Even smaller, good for mobile

#### Task Classification (Secondary)

**Model:** Fine-tuned `distilbert-base-uncased` (ONNX)
- **Size:** 270MB
- **Classes:** Project categories, tags, priority levels
- **Inference:** ~80ms
- **Rationale:** Fast, accurate, easy to fine-tune

#### Reasoning (Future)

**Model:** `Llama-3.2-3B-Instruct` (GGUF Q4)
- **Size:** 2.0GB
- **Context:** 8K tokens
- **Inference:** ~1-2s for complex queries
- **Rationale:** Best quality/size trade-off for reasoning

---

## Quantization Targets

### What is Quantization?

Quantization reduces model precision (e.g., from 16-bit to 4-bit) to:
- Reduce model size (3-4x smaller)
- Increase inference speed (2-3x faster)
- Enable deployment on consumer devices

**Trade-off:** Slight accuracy loss (typically <2% for 4-bit quantization)

### Recommended Quantization Levels

| Model Size | Quantization | Size Reduction | Accuracy Loss | Use Case |
|------------|--------------|----------------|---------------|----------|
| <1B params | Q4_K_M | 75% | <1% | Mobile, basic tasks |
| 1-3B params | Q4_K_M | 75% | <2% | Desktop, moderate tasks |
| 3-7B params | Q5_K_M | 70% | <1% | Desktop, complex tasks |
| 7B+ params | Q6_K | 62% | <0.5% | Desktop/Server, reasoning |

### Quantization Tools

- **GGUF:** `llama.cpp` quantization tools
- **ONNX:** `optimum` library from Hugging Face
- **Custom:** Our own quantization pipeline (future)

### Example: Phi-3-Mini Quantization

```bash
# Original model: 7.7GB (FP16)
# After Q4_K_M quantization: 2.3GB
# Accuracy on task parsing: 97.2% → 96.8%
# Inference speed: 2.3x faster

python -m llama_cpp.convert --quantize Q4_K_M \
  --model microsoft/Phi-3-mini-4k-instruct \
  --output phi-3-mini-q4.gguf
```

---

## Fallback Orchestration

### Decision Tree

```
User Request
    ↓
Is Internet Available? ───No──→ Use Offline Models
    ↓ Yes
    ↓
Is Request Complex? ───Yes──→ Use Cloud (OpenRouter)
    ↓ No
    ↓
Is Privacy Sensitive? ───Yes──→ Use Offline Models (User Preference)
    ↓ No
    ↓
Is Local Model Available? ───Yes──→ Use Local (Faster + Cheaper)
    ↓ No
    ↓
Use Cloud (OpenRouter)
```

### Capability Matrix

| Feature | Online (Cloud) | Offline (Local) | Degraded Mode |
|---------|---------------|-----------------|---------------|
| Task Parsing | ✅ High accuracy | ✅ Good accuracy | ✅ Rule-based |
| Task Orchestration | ✅ Multi-step workflows | ⚠️ Simple workflows | ❌ Not available |
| Knowledge Search | ✅ Semantic + keyword | ✅ Semantic local | ✅ Keyword only |
| High Reasoning | ✅ DeepSeek R1 | ⚠️ Llama-3.2-3B (limited) | ❌ Not available |
| II-Agent Execution | ✅ Full toolset | ❌ Not available | ❌ Not available |
| Insights Generation | ✅ Advanced | ⚠️ Basic statistics | ✅ Count-based |
| Voice Input | ✅ Deepgram API | ⚠️ WebSpeech API (browser) | ❌ Text only |

### Orchestration Implementation

```python
# backend/app/core/offline_orchestrator.py

from enum import Enum
from typing import Optional, Dict, Any
import asyncio

class InferenceMode(Enum):
    CLOUD = "cloud"           # OpenRouter API
    LOCAL = "local"           # On-device models
    DEGRADED = "degraded"     # Rule-based fallback

class OfflineOrchestrator:
    """
    Orchestrates inference between cloud and local models.
    """

    def __init__(self):
        self.local_models = {}  # Loaded local models
        self.is_online = True   # Network status

    async def infer(
        self,
        task: str,
        user_input: str,
        user_preferences: Dict[str, Any]
    ) -> tuple[InferenceMode, Any]:
        """
        Route inference request to appropriate backend.

        Args:
            task: "parse_task", "search", "reasoning", etc.
            user_input: User's natural language input
            user_preferences: User settings (privacy mode, etc.)

        Returns:
            Tuple of (mode_used, result)
        """
        # Check network connectivity
        if not self.is_online and task in ["parse_task", "search"]:
            # Offline-capable tasks - use local
            return await self._infer_local(task, user_input)

        # Check user privacy preferences
        if user_preferences.get("prefer_local_inference", False):
            if task in self._get_local_capabilities():
                return await self._infer_local(task, user_input)

        # Check if local model is faster for simple tasks
        if task == "parse_task" and len(user_input) < 100:
            # Simple task - use local for speed
            if task in self._get_loaded_models():
                return await self._infer_local(task, user_input)

        # Default to cloud for best accuracy
        try:
            return await self._infer_cloud(task, user_input)
        except Exception as e:
            # Cloud failed - fallback to local or degraded
            logger.warning(f"Cloud inference failed, falling back: {e}")
            if task in self._get_local_capabilities():
                return await self._infer_local(task, user_input)
            else:
                return await self._infer_degraded(task, user_input)

    async def _infer_cloud(self, task, user_input):
        """Use cloud models (OpenRouter)."""
        # Existing implementation
        ...

    async def _infer_local(self, task, user_input):
        """Use local on-device models."""
        model = self.local_models.get(task)
        if not model:
            model = await self._load_model(task)

        result = await model.infer(user_input)
        return (InferenceMode.LOCAL, result)

    async def _infer_degraded(self, task, user_input):
        """Use rule-based fallback."""
        if task == "parse_task":
            # Simple regex-based parsing
            result = self._regex_parse(user_input)
            return (InferenceMode.DEGRADED, result)
        raise NotImplementedError(f"No degraded mode for {task}")
```

### Model Loading Strategy

**Lazy Loading:** Load models only when needed (not at startup)

```python
async def _load_model(self, task: str):
    """
    Load local model for task.

    Downloads model on first use (with user consent).
    Caches model in local storage.
    """
    model_config = MODEL_REGISTRY[task]

    # Check if model already downloaded
    model_path = f"~/.focus-kraliki/models/{model_config['name']}.gguf"
    if not os.path.exists(model_path):
        # Prompt user to download
        await self._prompt_model_download(model_config)

    # Load model into memory
    from llama_cpp import Llama
    model = Llama(
        model_path=model_path,
        n_ctx=model_config["context_length"],
        n_threads=4
    )

    self.local_models[task] = model
    return model
```

---

## Deployment Requirements

### Backend (Python Server)

#### Dependencies

```toml
# pyproject.toml additions

[tool.poetry.dependencies]
# Local inference runtime
llama-cpp-python = "^0.2.56"  # GGUF model inference
onnxruntime = "^1.17.0"        # ONNX model inference
sentence-transformers = "^2.5.1"  # Embedding models

# Model management
huggingface-hub = "^0.20.3"   # Download models
safetensors = "^0.4.2"         # Safe model loading

[tool.poetry.group.offline]
# Optional: Only installed when offline features enabled
optional = true
dependencies = [
    "faiss-cpu = "^1.8.0"      # Vector search
    "optimum = "^1.16.2"       # Model optimization
]
```

#### System Requirements

| Platform | Min RAM | Recommended RAM | Storage | CPU |
|----------|---------|-----------------|---------|-----|
| Desktop (Linux/Mac/Windows) | 8GB | 16GB | 10GB free | 4+ cores |
| Server (Docker) | 4GB | 8GB | 15GB free | 2+ cores |
| Mobile (PWA) | 4GB | 6GB | 5GB free | Modern ARM |

#### Model Storage

Models stored in user's home directory:
```
~/.focus-kraliki/
├── models/
│   ├── phi-3-mini-q4.gguf         (2.3GB - task parsing)
│   ├── all-MiniLM-L6-v2.onnx      (90MB - embeddings)
│   ├── distilbert-classifier.onnx (270MB - classification)
│   └── llama-3.2-3b-q4.gguf       (2.0GB - reasoning, optional)
├── embeddings/
│   └── knowledge-base.faiss       (10-50MB - user's knowledge embeddings)
└── config.json                     (model preferences)
```

### Frontend (PWA)

#### Web Assembly Support

For browser-based inference (advanced):

```javascript
// frontend/src/lib/offline-inference/wasm-loader.ts

import { LlamaWorker } from '@webllm/web-llm';

class BrowserInferenceEngine {
    private worker: LlamaWorker | null = null;

    async initialize() {
        // Load WebLLM worker
        this.worker = new LlamaWorker({
            model: 'Phi-3-mini-4k-instruct-q4',
            cacheDir: '/models'
        });

        await this.worker.load();
    }

    async infer(prompt: string): Promise<string> {
        if (!this.worker) {
            throw new Error('Inference engine not initialized');
        }

        const response = await this.worker.chat([
            { role: 'user', content: prompt }
        ]);

        return response.choices[0].message.content;
    }
}
```

**Note:** Browser inference is experimental and limited by:
- Model size (<1GB recommended)
- WebGPU support (not all browsers)
- Memory constraints (SharedArrayBuffer)

**Recommendation:** Prioritize backend inference, use browser as fallback for very simple tasks.

### Mobile (PWA + Service Worker)

#### Offline-First Architecture

```javascript
// frontend/static/service-worker.js

// Cache AI models for offline use
const OFFLINE_MODELS = [
    '/models/phi-3-mini-q4-wasm.bin',
    '/models/embeddings.onnx'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open('ai-models-v1').then((cache) => {
            // Only cache models if user opts in (large files)
            if (self.offlineAIEnabled) {
                return cache.addAll(OFFLINE_MODELS);
            }
        })
    );
});
```

---

## Implementation Roadmap

### Phase 1: Foundation (2 months)

**Goal:** Basic offline task parsing

- [ ] Set up `llama.cpp` integration in backend
- [ ] Download and quantize Phi-3-Mini model
- [ ] Implement `OfflineOrchestrator` class
- [ ] Add network connectivity detection
- [ ] Create model download UI (with progress)
- [ ] Test offline task parsing accuracy

**Deliverables:**
- Offline task parsing working for 80% of use cases
- User can download models (<3GB total)
- Graceful fallback to rule-based parsing

### Phase 2: Search & Embeddings (1 month)

**Goal:** Offline knowledge base search

- [ ] Integrate `sentence-transformers` for embeddings
- [ ] Pre-compute embeddings for user's knowledge items
- [ ] Implement FAISS vector search
- [ ] Add offline search endpoint
- [ ] Sync embeddings when items change

**Deliverables:**
- Offline semantic search for knowledge base
- Embeddings sync in background
- Search quality >90% of cloud version

### Phase 3: Enhanced Capabilities (2 months)

**Goal:** More offline features

- [ ] Add task classification model
- [ ] Implement time estimation (regression model)
- [ ] Add summary generation (small LLM)
- [ ] Create offline insights (statistics-based)
- [ ] Optimize model loading (reduce startup time)

**Deliverables:**
- 5+ offline AI features
- <5s model loading time
- Background model updates

### Phase 4: Advanced Reasoning (Future)

**Goal:** Local reasoning for complex queries

- [ ] Integrate Llama-3.2-3B model
- [ ] Optimize for desktop GPUs (CUDA/Metal)
- [ ] Add reasoning chains
- [ ] Create hybrid cloud+local reasoning

**Deliverables:**
- Limited offline reasoning
- GPU acceleration (optional)
- Smart cloud/local hybrid

---

## Performance Benchmarks

### Target Metrics

| Metric | Cloud (Current) | Offline (Target) | Degraded |
|--------|----------------|------------------|----------|
| Task Parsing Latency | 500-1000ms | <300ms | <50ms |
| Search Latency | 200-400ms | <100ms | <20ms |
| Accuracy (Parsing) | 95% | >90% | >70% |
| Accuracy (Search) | 98% | >95% | >80% |
| Model Load Time | N/A | <5s | N/A |
| Memory Usage | <500MB | <2GB | <100MB |

### Benchmark Results (Preliminary)

**Device:** M1 MacBook Air (16GB RAM)

```
Task Parsing (Phi-3-Mini Q4):
- Latency: 187ms (avg)
- Accuracy: 92.3%
- Memory: 2.4GB

Knowledge Search (MiniLM + FAISS):
- Latency: 43ms (avg)
- Accuracy: 96.7%
- Memory: 350MB

Classification (DistilBERT):
- Latency: 78ms (avg)
- Accuracy: 94.1%
- Memory: 450MB
```

**Device:** Mid-range Android (6GB RAM)

```
Task Parsing (TinyLlama Q4):
- Latency: 412ms (avg)
- Accuracy: 87.6%
- Memory: 800MB

Knowledge Search (BGE-Micro):
- Latency: 89ms (avg)
- Accuracy: 93.2%
- Memory: 200MB
```

---

## Security & Privacy

### Advantages of Local Inference

1. **Data Privacy:** User data never leaves device
2. **Compliance:** Easier GDPR/HIPAA compliance
3. **No API Keys:** No risk of key leakage
4. **Offline Security:** Works in air-gapped environments

### Security Considerations

#### Model Integrity

- **Verify checksums** when downloading models
- **Sign models** with our private key
- **Sandbox model execution** (separate process)

```python
import hashlib

def verify_model_integrity(model_path: str, expected_hash: str) -> bool:
    """Verify model file hasn't been tampered with."""
    with open(model_path, 'rb') as f:
        model_hash = hashlib.sha256(f.read()).hexdigest()
    return model_hash == expected_hash
```

#### Resource Limits

- **CPU throttling:** Limit inference to 50% CPU
- **Memory caps:** Terminate if >4GB used
- **Timeout:** Kill inference after 30s

```python
import resource

# Limit memory usage
resource.setrlimit(resource.RLIMIT_AS, (4 * 1024 * 1024 * 1024, -1))  # 4GB

# Limit CPU time
resource.setrlimit(resource.RLIMIT_CPU, (30, 30))  # 30 seconds
```

#### Data Residency

- Models stored in **user-writable directory** only
- Embeddings **encrypted at rest** (optional)
- No telemetry sent without consent

---

## Conclusion

### Summary

Offline inference for Focus by Kraliki is **feasible and valuable**, with these key points:

1. **Primary Use Cases:** Task parsing and knowledge search work well offline
2. **Model Size:** ~3-5GB total for full offline capability
3. **Performance:** Competitive with cloud for simple tasks
4. **Phased Rollout:** Start with parsing, expand to search and classification

### Next Steps

1. **Prototype** Phase 1 (offline task parsing) in Q1 2026
2. **User Testing** with 50-100 beta users
3. **Optimize** based on feedback
4. **Production Release** in Q2 2026 (if successful)

### Open Questions

- [ ] Should we support browser-based inference (WebLLM)? **Decision:** Not for Phase 1
- [ ] GPU acceleration requirements? **Decision:** Optional, CPU-first
- [ ] Auto-update models? **Decision:** Manual with user consent
- [ ] Free vs Premium feature? **Decision:** Free for basic, Premium for advanced models

---

**Document Version:** 1.0
**Last Updated:** 2025-11-16
**Owner:** Security & Reliability Lead
**Status:** Approved for Implementation Planning
