# Fase 3: External Knowledge Integration

**Status**: ✅ Completada  
**Fecha**: 2026-05-06  
**Branch**: `feature/gfl-formalization-v2`

---

## Resumen Ejecutivo

La Fase 3 integra GeneForgeLang (GFL) IR con fuentes de conocimiento externas:
- **OpenMed**: Embeddings biomédicos, NER clínico, privacy filter (RFC 002)
- **HuggingScience**: Modelos de razonamiento científico
- **PubMed**: Literatura científica

**Principio arquitectónico**: GFL mantiene la autoridad semántica (ground truth). Las fuentes externas son *observation providers* (Axis 3 per TRANSFER_MEMORANDUM.md).

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                     GFL IR Core                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   State     │  │  Reasoning  │  │      KnowledgeBase      │  │
│  │             │  │    Loop     │  │   (local + external)    │  │
│  └──────┬──────┘  └──────┬──────┘  └───────────┬─────────────┘  │
└─────────┼────────────────┼─────────────────────┼────────────────┘
          │                │                     │
          ▼                ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│              RetrievalService (Unified Interface)                 │
│     ┌───────────────┐         ┌─────────────────────────┐         │
│     │  retrieve()   │◄──────►│    combine_confidence() │         │
│     │  enrich()     │         │    synthesize()         │         │
│     └───────┬───────┘         └─────────────────────────┘         │
└─────────────┼─────────────────────────────────────────────────────┘
              │
     ┌────────┴────────┐
     ▼                 ▼
┌────────────┐   ┌──────────────┐
│  OpenMed   │   │ HuggingScience│
│  Connector │   │   Connector   │
├────────────┤   ├──────────────┤
│• Embeddings│   │• Reasoning    │
│• NER       │   │• QA           │
│• Privacy   │   │• Synthesis    │
│• Literature│   │               │
└────────────┘   └──────────────┘
```

---

## Componentes

### 1. OpenMed Connector

**Ubicación**: `src/geneforgelang/ir/external/openmed_connector.py`

**Funcionalidades**:

| Método | Descripción | Producción |
|--------|-------------|------------|
| `get_embedding(entity_id)` | Obtiene embedding biomédico | OpenMed API |
| `find_similar_entities()` | Entidades similares por embeddings | OpenMed API |
| `extract_entities(text)` | NER en texto clínico | `openmed-clinical-ner` |
| `deidentify_clinical_note()` | De-identificación PII | `privacy-filter-nemotron` |
| `search_literature()` | Búsqueda PubMed | NCBI Entrez |

**RFC 002 Compliance**:
```python
result = connector.deidentify_clinical_note(clinical_text)
# result["privacy_cleared"] = True  <- Flag requerido por MRI
```

### 2. HuggingScience Connector

**Ubicación**: `src/geneforgelang/ir/external/huggingscience_connector.py`

**Funcionalidades**:

| Método | Descripción | Modelo Referencia |
|--------|-------------|-------------------|
| `reason_about_hypothesis()` | Razonamiento científico | BioGPT / MedAlpaca |
| `synthesize_evidence()` | Síntesis de evidencia múltiple | Custom pipeline |
| `answer_question()` | QA biomédico | BioGPT |
| `batch_reason()` | Procesamiento batch | - |

**Ejemplo**:
```python
connector = HuggingScienceConnector()
result = connector.reason_about_hypothesis(
    "Knockout TP53 in cancer cells"
)
# result.confidence: 0.92
# result.conclusion: "TP53 knockout likely disrupts apoptosis..."
```

### 3. RetrievalService

**Ubicación**: `src/geneforgelang/ir/external/retrieval_service.py`

**API Principal**:

```python
service = RetrievalService(
    enable_openmed=True,
    enable_huggingscience=True
)

# Para un objetivo biológico
context = service.retrieve_for_objective(
    objective=Objective(
        description="Knockout TP53",
        target_entity="TP53"
    ),
    state=biological_state
)

# Contexto incluye:
# - similar_entities: [SimilarEntity, ...]
# - literature_evidence: [dict, ...]
# - reasoning_result: ReasoningResult
# - combined_confidence: float
```

### 4. KnowledgeBase Extendido

**Ubicación**: `src/geneforgelang/ir/knowledge_grounding.py`

**Nuevos Capacidades**:

```python
# Configuración
retrieval = RetrievalService(enable_openmed=True)
kb = KnowledgeBase(
    retrieval_service=retrieval,
    enable_external=True  # Opt-in
)

# Query mergeada (local + external)
info = kb.query("TP53")
# info["sources"] = ["curated", "openmed"]

# Retrieval para objetivo
result = kb.retrieve_for_objective(objective)

# Enriquecimiento de estado
enriched_state = kb.enrich_with_retrieval(state)
```

---

## Flujo de Datos

### Caso 1: Reasoning Loop con Retrieval

```python
# 1. Inicializar componentes
kb = KnowledgeBase(retrieval_service=RetrievalService(), enable_external=True)
loop = ReasoningLoop(planner=..., evaluator=..., knowledge_base=kb)

# 2. Ejecutar
result = loop.run(state, objective)

# Internamente:
# a. Planner genera estrategia
# b. Executor aplica instrucciones
# c. Evaluator puntuar estado
# d. KnowledgeBase.retrieve_for_objective() enriquece contexto
# e. Loop revisa basado en evidencia retrieval
```

### Caso 2: Validación de Hipótesis

```python
# Hipótesis: "BRCA1 knockout is lethal"
hypothesis = "Knockout BRCA1 in homologous_repair_context"

# 1. Retrieval de evidencia
context = service.retrieve_for_objective(
    Objective(description=hypothesis, target_entity="BRCA1")
)

# 2. Razonamiento
reasoning = connector.reason_about_hypothesis(hypothesis)

# 3. Validación
if context.combined_confidence > 0.8 and reasoning.confidence > 0.7:
    viability = "supported"
else:
    viability = "requires_experimental_validation"
```

---

## Interfaces Públicas

### Exports del Módulo IR

```python
from geneforgelang.ir import (
    # Fase 3: External Knowledge
    OpenMedConnector,
    HuggingScienceConnector,
    RetrievalService,
    RetrievedEvidence,
)
```

### Dataclasses Principales

```python
@dataclass
class SimilarEntity:
    entity_id: str
    entity_type: str
    similarity: float  # 0-1
    metadata: dict

@dataclass
class ReasoningResult:
    conclusion: str
    confidence: float
    evidence: list[dict]
    reasoning_chain: list[str]

@dataclass
class RetrievalContext:
    objective: Objective
    target_entity: Optional[str]
    similar_entities: list[SimilarEntity]
    literature_evidence: list[dict]
    reasoning_result: Optional[ReasoningResult]
    combined_confidence: float
```

---

## Tests

**Suite**: `tests/unit/ir/test_external_connectors.py`

```bash
pytest tests/unit/ir/test_external_connectors.py -v
```

**Cobertura**:
- OpenMedConnector: 8 tests
- HuggingScienceConnector: 5 tests
- RetrievalService: 6 tests
- KnowledgeBase integration: 5 tests

**Total IR Tests**: 74 passed

---

## Configuración

### Entorno de Desarrollo

```python
# Mock implementations (default)
connector = OpenMedConnector()  # No API key required
connector = HuggingScienceConnector()  # Local inference simulated
```

### Entorno de Producción

```python
# Con APIs reales
connector = OpenMedConnector(
    api_key=os.environ["OPENMED_API_KEY"],
    base_url="https://api.openmed.fdn.org/v1"
)

connector = HuggingScienceConnector(
    api_token=os.environ["HF_TOKEN"],
    model_name="microsoft/biogpt"
)
```

---

## Roadmap Fase 4

1. **Cache Persistente**: Redis/ChromaDB para embeddings
2. **Rate Limiting**: Gestión de cuotas API
3. **Async Retrieval**: `retrieve_for_objective_async()`
4. **Feedback Loop**: Aprendizaje de retrieval exitoso
5. **Multi-hop Reasoning**: Chain-of-thought sobre KG

---

## Referencias

- `OPENMED_ADAPTER.md`: Especificación de integración
- `RFC-002-openmed-privacy-layer.md`: Privacy layer
- `demo_ir.py`: Demos 7-10 (Fase 3)
