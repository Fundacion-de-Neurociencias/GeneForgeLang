# Fase 4: Advanced Retrieval & Integration

**Status**: ✅ Completada  
**Fecha**: 2026-05-06  
**Branch**: `feature/gfl-formalization-v2`

---

## Resumen Ejecutivo

La Fase 4 añade capacidades avanzadas de retrieval e integración con el ecosistema existente:

1. **Persistent Cache Layer**: ChromaDB para embeddings y resultados
2. **Async Retrieval**: Operaciones no-bloqueantes con prefetching
3. **Feedback Loop**: Aprendizaje de calidad de retrieval
4. **Multi-hop Reasoning**: Razonamiento a través de grafos de entidades
5. **RAG Bridge**: Integración con `gfl-plugin-rag-engine` existente

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         GFL IR + Fase 3/4                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │  Async       │  │  Feedback    │  │  Multi-Hop   │  │   RAG       │ │
│  │  Retrieval   │  │  Loop        │  │  Reasoner    │  │   Bridge    │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬──────┘ │
└─────────┼────────────────┼────────────────┼────────────────┼──────────┘
          │                │                │                │
          ▼                ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Fase 4 Cache Layer (ChromaDB)                        │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  L1: Memory Cache (hot data)                                    │    │
│  │  L2: ChromaDB Persistent (embeddings, literature, reasoning)  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│              gfl-plugin-rag-engine (Ecosystem Integration)              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │  ChromaDB       │  │  PubMed         │  │  Hypothesis     │         │
│  │  Collection     │  │  Entrez         │  │  Validation     │         │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Componentes

### 1. EmbeddingCache (Persistent Cache)

**Ubicación**: `src/geneforgelang/ir/fase4/cache_layer.py`

**Arquitectura de 2 niveles**:
- **L1**: In-memory cache (dict) - acceso rápido
- **L2**: ChromaDB persistente - durabilidad

**API**:
```python
from geneforgelang.ir.fase4 import EmbeddingCache, CacheConfig

config = CacheConfig(
    db_path="./gfl_cache",
    collection_name="embeddings",
    max_entries=10000,
)
cache = EmbeddingCache(config)

# Cache embedding
cache.put_embedding("TP53", embedding_vector, metadata={"function": "tumor_suppressor"})

# Cache literature
cache.put_literature("TP53 AND cancer", pubmed_results)

# Cache reasoning
cache.put_reasoning("knockout TP53 hypothesis", reasoning_result)
```

### 2. AsyncRetrievalService

**Ubicación**: `src/geneforgelang/ir/fase4/async_retrieval.py`

**Capacidades**:
- `retrieve_for_objective_async()` - Non-blocking retrieval
- `batch_retrieve_async()` - Concurrent multi-objective retrieval
- `retrieve_from_all_sources()` - Parallel OpenMed + HuggingScience
- Background prefetching

**Ejemplo**:
```python
from geneforgelang.ir.fase4 import AsyncRetrievalService

service = AsyncRetrievalService()

# Non-blocking retrieval
result = await service.retrieve_for_objective_async(objective)
print(f"Retrieved in {result.elapsed_ms}ms (cache_hit={result.cache_hit})")

# Concurrent multi-source
results = await service.retrieve_from_all_sources(
    "TP53",
    include_similar=True,
    include_literature=True,
    include_reasoning=True,
)
```

### 3. FeedbackStore (Learning)

**Ubicación**: `src/geneforgelang/ir/fase4/feedback_loop.py`

**Funcionalidad**:
- Registra éxito/fracaso de cada retrieval
- Métricas de calidad por tipo de query
- Sugerencias de mejora basadas en historial
- Best practices extraction

**Uso**:
```python
from geneforgelang.ir.fase4 import FeedbackStore, RetrievalFeedback

store = FeedbackStore("./feedback.jsonl")

# Record feedback
store.record(RetrievalFeedback(
    query="TP53 knockout",
    query_type="entity",
    success=True,
    confidence_score=0.92,
    retrieval_time_ms=150,
))

# Get stats
stats = store.get_stats("entity")
# {"count": 45, "success_rate": 0.89, "avg_confidence": 0.78}

# Get suggestions
suggestions = store.suggest_improvements("TP53 knockdown", "entity")
# ["High failure rate detected - consider alternative query formulation"]
```

### 4. MultiHopReasoner

**Ubicación**: `src/geneforgelang/ir/fase4/multi_hop.py`

**Razonamiento a través de grafos biológicos**:
- Pathway traversal
- Interaction chains
- Causal reasoning

**Algoritmos**:
1. **Direct multi-hop**: Exploración secuencial del grafo
2. **Via interactors**: Caminos a través de interactores comunes
3. **Via pathway**: Conexión por membresía de pathway

**API**:
```python
from geneforgelang.ir.fase4 import MultiHopReasoner

reasoner = MultiHopReasoner(max_hops=3)

# Find paths between entities
paths = reasoner.find_paths("TP53", "MDM2", state, max_paths=3)

# Explain relationship
explanation = reasoner.explain_relationship("TP53", "KRAS")
# {
#   "relationship": "regulatory",
#   "confidence": 0.72,
#   "path": ["TP53", "MDM2", "KRAS"],
#   "explanation": "TP53 regulates MDM2 which interacts with KRAS..."
# }
```

### 5. RAGBridge (Ecosystem Integration)

**Ubicación**: `src/geneforgelang/ir/fase4/rag_bridge.py`

**Integra IR con `gfl-plugin-rag-engine`**:
- Valida objetivos IR contra evidencia RAG
- Enriquece estados con literatura RAG
- Query directo a ChromaDB del plugin

**API**:
```python
from geneforgelang.ir.fase4 import RAGBridge, RAGIntegration

# Direct bridge
bridge = RAGBridge(
    rag_plugin_path="./gfl-plugin-rag-engine",
    chroma_db_path="./chroma_db",
)

# Validate objective via RAG
validation = bridge.validate_objective(objective)
print(f"RAG validation: {validation.is_valid} (confidence: {validation.confidence})")

# High-level integration
integration = RAGIntegration(retrieval_service, bridge)
comprehensive = integration.retrieve_comprehensive(objective)
# Combines IR + RAG evidence
```

---

## Flujos de Datos

### Caso 1: Async Retrieval con Cache

```python
# 1. Inicializar
async_service = AsyncRetrievalService(
    retrieval_service=RetrievalService(),
    cache=EmbeddingCache(),
)

# 2. Start background prefetching
async_service.start_prefetching()

# 3. Queue entities for prefetch
async_service.queue_prefetch("TP53")
async_service.queue_prefetch("KRAS")

# 4. Async retrieval (may hit cache)
result = await async_service.retrieve_for_objective_async(objective)

# 5. Record feedback
feedback_store.record(RetrievalFeedback(
    query=objective.description,
    success=result.context is not None,
    elapsed_ms=result.elapsed_ms,
))
```

### Caso 2: Multi-hop + RAG Integration

```python
# 1. Build reasoning path
reasoner = MultiHopReasoner(max_hops=3)
path = reasoner.reason_across_path("TP53", "MDM2", state)

# 2. Validate each hop via RAG
for hop in path.hops:
    validation = rag_bridge.validate_objective(
        Objective(description=f"Analyze {hop.entity_id}")
    )
    hop.rag_confidence = validation.confidence

# 3. Combined confidence
overall = min(hop.rag_confidence for hop in path.hops) * path.overall_confidence
```

---

## Tests

**Suite**: `tests/unit/ir/test_fase4.py`

```bash
pytest tests/unit/ir/test_fase4.py -v
```

**Cobertura**:
- EmbeddingCache: 5 tests
- AsyncRetrievalService: 4 tests (incl. async)
- FeedbackStore: 5 tests
- MultiHopReasoner: 6 tests
- RAGBridge: 5 tests
- RAGIntegration: 2 tests

**Total IR Tests**: 99 passed (Fase 1-4)

---

## Integración con Ecosistema

### Con gfl-plugin-rag-engine

```
GFL IR Fase 4                    gfl-plugin-rag-engine
┌──────────────────┐              ┌─────────────────────────┐
│ RAGBridge        │─────────────►│ RAGEnginePlugin         │
│ ├─ validate()    │   (import)   │ ├─ run()               │
│ ├─ query_lit()   │              │ └─ _query_knowledge()  │
│ └─ enrich()      │              └─────────────────────────┘
└──────────────────┘                         │
                                             ▼
                                    ┌────────────────┐
                                    │ ChromaDB       │
                                    │ (biomedical_   │
                                    │  _literature)  │
                                    └────────────────┘
```

### Flujo Completo

```python
# 1. Define objective in IR
objective = Objective(
    description="Validate TP53-MDM2 interaction",
    target_entity="TP53",
)

# 2. Multi-hop reasoning
reasoner = MultiHopReasoner()
path = reasoner.find_paths("TP53", "MDM2", state)

# 3. IR external knowledge
ir_context = retrieval_service.retrieve_for_objective(objective)

# 4. RAG validation
rag = RAGBridge()
rag_validation = rag.validate_objective(objective)
rag_evidence = rag.query_literature("TP53 MDM2 interaction")

# 5. Combine
combined = {
    "path": path.to_chain(),
    "ir_confidence": ir_context.combined_confidence,
    "rag_confidence": rag_validation.confidence,
    "evidence": rag_evidence + ir_context.literature_evidence,
}
```

---

## Configuración

### Producción

```python
# Cache persistente
from geneforgelang.ir.fase4 import CacheConfig, EmbeddingCache

config = CacheConfig(
    db_path="/var/lib/geneforge/cache",
    max_entries=100000,
    ttl_seconds=86400,  # 24h
)

# Async service con prefetching
async_service = AsyncRetrievalService(
    retrieval_service=RetrievalService(),
    cache=EmbeddingCache(config),
    max_workers=8,
)

# Feedback store persistente
feedback = FeedbackStore("/var/lib/geneforge/feedback.jsonl")

# RAG bridge con plugin
rag = RAGBridge(
    rag_plugin_path="/opt/geneforge/plugins/gfl-plugin-rag-engine",
    chroma_db_path="/var/lib/geneforge/chroma_db",
)
```

---

## Roadmap Fase 5

1. **Distributed Cache**: Redis cluster para multi-nodo
2. **Real-time Sync**: WebSocket updates de literatura nueva
3. **ML-based Ranking**: Modelo entrenado con feedback
4. **GraphQL API**: Query interface para multi-hop
5. **Visualization**: Export de paths a Cytoscape/D3

---

## Referencias

- `FASE3.md`: External knowledge integration
- `test_fase4.py`: Test suite completo
- `gfl-plugin-rag-engine/README.md`: Plugin documentation
