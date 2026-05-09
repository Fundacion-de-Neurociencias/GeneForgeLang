# Plan de Implementación: Hard Validation Layer (HVL)
## Repositorio: GeneForgeLang (Lenguaje)
**Estado**: Pendiente de revisión por coordinadores
**Versión del plan**: 2.0
**Fecha**: 2026-05-09
**Requiere coordinación con**: GeneForge (repositorio hermano)

---

## Contexto y motivación

GeneForgeLang (GFL) es la autoridad formal del ecosistema: define invariantes, semántica, contratos y límites del espacio de estados biológico. **GFL no ejecuta inferencia. GFL no aprende. GFL no valida empíricamente.**

Este plan introduce tres cambios en GFL:

1. **Especificación formal de la HVL** (`docs/spec/HVL.md`) — define el contrato que GeneForge debe implementar
2. **Exportación de invariantes como artefacto compilado** (`spec/invariant_manifest.json`) — para consumo operacional por la HVL
3. **Deprecación explícita de PFUL y ERC** — documentos que contradicen la separación epistemológica que la HVL requiere

GFL no implementa la HVL. GFL define su contrato y exporta los invariantes que la HVL necesita para operar.

---

## Corrección epistemológica central

La CONSTITUTION.md actual dice:

> "GFL = The Constitution: Defines the rules, semantics, and state space."

Esto es correcto pero incompleto. Debe añadirse explícitamente:

> **"GFL defines formal validity, not biological truth."**

Esta distinción es crítica. GFL define qué es *formalmente válido* dentro del lenguaje. No define qué es *biológicamente verdadero*. La HVL es precisamente la capa que confronta los outputs formalmente válidos con evidencia biológica externa. Si GFL reclamara autoridad sobre la verdad biológica, la HVL sería imposible epistemológicamente.

---

## Cambios propuestos

### A1 — Crear `docs/spec/HVL.md`

Especificación formal de la Hard Validation Layer desde la perspectiva de GFL.

**Contenido**:

**1. Definición y mandato**
La HVL es una capa de falsificación externa al motor causal. Su función es confrontar outputs de GeneForge con evidencia empírica externa y con los invariantes formales de GFL. La HVL no modifica el motor causal, no reescribe reglas, no corrige inferencias.

**2. Los 5 pilares**

| Pilar | Descripción |
|-------|-------------|
| Semantic Validity | Verificación contra invariantes GFL exportados |
| Evidence Quality Assessment | Evaluación de calidad de fuentes externas antes de usarlas |
| External Evidence Alignment | Detección de divergencias con evidencia externa de calidad |
| Predictive Calibration | Tracking de calibración con distinción ground truth / proxy operacional |
| Drift Detection | Detección de degradación con doble referencia |

**3. Regla de prioridad**
`GFL invariants > HVL empirical anomalies`

Si evidencia empírica contradice un invariante GFL → `ANOMALY_RECORD` + `EPISTEMIC_REVIEW_REQUIRED`. Nunca auto-modificación del invariante. Si la contradicción es sistemática y de alta calidad → trigger de GFL-RFC formal.

**4. Estados de salida HVL**

| Estado | Significado |
|--------|-------------|
| `SAFE` | Output alineado con invariantes y evidencia disponible |
| `RESTRICTED` | Divergencias menores; uso con supervisión |
| `RESEARCH_ONLY` | Divergencias significativas; no apto para uso clínico/operacional |
| `UNSAFE` | Violación de invariantes o divergencia sistemática; requiere revisión humana obligatoria |

**5. Non-Intervention Principle**
La HVL puede observar, clasificar, restringir e invalidar outputs. **Nunca** puede participar en generación causal, generación de probabilidades, propagación causal u optimización de intervenciones.

**6. Mandato de no-corrección**
La HVL no corrige. Si detecta un problema, lo registra y clasifica. La corrección es responsabilidad del proceso de revisión humana o de un GFL-RFC.

---

### A2 — Actualizar `docs/spec/INVARIANT_BOUNDARIES.md`

El documento actual describe el Immutable Core y el Learning Sandbox (PFUL). Con la deprecación de PFUL, el documento debe actualizarse para reflejar:

**Cambios**:
- Eliminar referencias a PFUL como capa activa
- Añadir sección: "Protección frente a loops de auto-modificación" — el Immutable Core está protegido de cualquier mecanismo de auto-modificación, incluyendo los descritos en PFUL (ahora deprecado)
- Añadir referencia a HVL como mecanismo de falsificación *externo* (no interno)
- Clarificar: la HVL nunca puede modificar el Immutable Core, ni siquiera indirectamente

**Sección a añadir**:
```
## 5. Relación con la HVL

La Hard Validation Layer (HVL) opera como capa de falsificación externa.
A diferencia de PFUL (deprecado), la HVL no modifica ningún componente del
sistema. Si la HVL detecta una contradicción sistemática con un invariante
del Immutable Core, el mecanismo de respuesta es un GFL-RFC, nunca una
actualización interna.

La HVL tiene acceso de lectura al invariant_manifest exportado.
No tiene acceso de escritura a ningún componente de GFL.
```

---

### A3 — Actualizar `CONSTITUTION.md`

**Cambios**:

1. Añadir en §1 o §2:
   > "GFL defines formal validity, not biological truth. The HVL is the external layer that confronts formally valid outputs with empirical evidence."

2. Introducir HVL como capa de falsificación externa en el diagrama de responsabilidades:
   ```
   GFL (Legislative) → GeneForge (Executive) → HVL (External Falsification) → Human Governance
   ```

3. Añadir en §3 (Structural Boundary):
   > "GeneForge must implement the HVL as defined in docs/spec/HVL.md. The HVL operates outside the causal pipeline and never modifies GFL semantics or GeneForge inference logic."

---

### A4 — Deprecar `docs/spec/PFUL.md` y `docs/spec/ERC.md`

**Acción**: mover ambos archivos a `docs/deprecated/` con banner `NON-CANONICAL`.

**Razón para PFUL**:
PFUL describe un loop de auto-modificación epistemológica (ajuste de pesos de CAL, heurísticas de GeneForge basado en outcomes observados). Esto contradice directamente la HVL: si el sistema puede auto-modificarse basándose en evidencia empírica, la HVL no puede ser una capa de falsificación externa estable. PFUL y HVL son incompatibles filosóficamente.

**Razón para ERC**:
ERC describe a CAL como "Conflict Registrar" con capacidad de ajustar prioridades. Parte de su lógica (preservación de tensiones irreducibles, prohibición de resolución silenciosa) es valiosa y se absorbe en HVL.md. La parte que implica ajuste dinámico de pesos queda deprecada junto con PFUL.

**Banner a añadir en ambos archivos**:
```markdown
> ⚠️ **NON-CANONICAL — DEPRECADO**
> Este documento ha sido deprecado en la versión [X.Y] de GFL.
> Motivo: conflicto con el Non-Intervention Principle de la HVL y con
> los principios de falsabilidad fuerte del ecosistema.
> Referencia: docs/spec/HVL.md, docs/spec/INVARIANT_BOUNDARIES.md
> Este archivo se conserva por razones históricas. No debe usarse como
> referencia para implementaciones nuevas.
```

**Crear `docs/deprecated/README.md`** explicando el proceso de deprecación y por qué estos documentos entran en conflicto con la arquitectura actual.

---

### A5 — Crear `spec/invariant_manifest.json`

Este es el artefacto más importante de este plan para la interoperabilidad con GeneForge.

**Propósito**: exportar los invariantes GFL como artefacto compilado que la HVL de GeneForge pueda consumir directamente, sin necesidad de interpretar GFL ni usar la conformance suite.

**Distinción crítica**:
- La **conformance suite** (`tests/conformance_suite/`) verifica que una *implementación* respeta el estándar GFL. Es para testing.
- El **invariant manifest** es un contrato operacional: lista de invariantes que cualquier output debe respetar. Es para runtime.

**Estructura propuesta**:
```json
{
  "gfl_version": "2.x.x",
  "manifest_version": "1.0.0",
  "generated_at": "ISO-8601 timestamp",
  "invariants": [
    {
      "id": "INV-001",
      "name": "IUPAC_INTEGRITY",
      "description": "Nucleotide sequences must use valid IUPAC codes",
      "category": "semantic",
      "severity": "CRITICAL",
      "check_type": "pattern_match",
      "parameters": { "allowed_chars": "ACGTURYSWKMBDHVN-" }
    },
    {
      "id": "INV-002",
      "name": "CENTRAL_DOGMA_DIRECTION",
      "description": "Transcription must follow DNA→RNA direction",
      "category": "causal",
      "severity": "CRITICAL",
      "check_type": "causal_direction"
    }
  ]
}
```

**Proceso de generación**: el manifest debe generarse automáticamente desde la fuente de verdad de invariantes GFL, no mantenerse manualmente. Añadir script `scripts/export_invariant_manifest.py`.

**Versionado**: el manifest debe versionarse junto con GFL. Un cambio en invariantes implica una nueva versión del manifest.

---

### A6 — Expandir taxonomía de errores en `src/geneforgelang/core/errors.py`

Añadir una nueva categoría `HVL` y los códigos de error formales que GeneForge usará en sus `HVLFinding`.

**Nueva categoría**:
```python
class ErrorCategory(str, Enum):
    # ... categorías existentes ...
    HVL = "hvl"  # Hard Validation Layer findings
```

**Nuevos códigos**:
```python
class ErrorCodes:
    # ... códigos existentes ...

    # HVL findings (HVL001-HVL099)
    HVL_SEMANTIC_VIOLATION    = "HVL001"  # Output viola invariante GFL
    HVL_EMPIRICAL_ANOMALY     = "HVL002"  # Divergencia con evidencia externa
    HVL_UNCALIBRATED          = "HVL003"  # Calibración fuera de umbral
    HVL_DRIFT_DETECTED        = "HVL004"  # Degradación detectada
    HVL_EVIDENCE_QUALITY_LOW  = "HVL005"  # Fuente externa no alcanza umbral
    HVL_UNSAFE_OUTPUT         = "HVL006"  # Estado UNSAFE: revisión humana obligatoria
    HVL_MANIFEST_UNAVAILABLE  = "HVL007"  # invariant_manifest no disponible
    HVL_ANOMALY_RECORD        = "HVL008"  # Contradicción invariante-empírica registrada
```

**Notas para coordinadores**:
- Estos códigos son la interfaz formal entre GFL y GeneForge para la HVL.
- GeneForge los usa en sus `HVLFinding`; GFL los define como parte del estándar.
- Añadir a `__all__` y documentar en el módulo.

---

### A7 — Congelar expansión conceptual en GFL

A partir de la aprobación de este plan, GFL no acepta nuevas especificaciones que no sean:

- Actualizaciones al contrato HVL (`docs/spec/HVL.md`)
- Actualizaciones al invariant export contract (`spec/invariant_manifest.json`)
- Actualizaciones a la taxonomía de errores HVL (`errors.py`)
- GFL-RFCs formales para cambios en invariantes del Immutable Core

Cualquier propuesta que introduzca lógica de calibración, drift detection, evidence quality, o aprendizaje adaptativo en GFL debe ser rechazada. Esas responsabilidades pertenecen a GeneForge/HVL.

---

## Gestión de PFUL, ERC y CAL

| Documento | Acción | Justificación |
|-----------|--------|---------------|
| `docs/spec/PFUL.md` | Mover a `docs/deprecated/PFUL.md` + banner NON-CANONICAL | Loop de auto-modificación incompatible con HVL |
| `docs/spec/ERC.md` | Mover a `docs/deprecated/ERC.md` + banner NON-CANONICAL | Ajuste dinámico de pesos incompatible con Non-Intervention Principle |
| Referencias a CAL | Mantener como concepto documental histórico, no operativo | CAL como "Conflict Registrar" queda absorbido en HVL.md |
| `INVARIANT_BOUNDARIES.md` | Actualizar (ver A2) | Reflejar deprecación de PFUL y protección del Immutable Core |

---

## Separación de responsabilidades (tabla de referencia)

| Responsabilidad | GFL | GeneForge/HVL |
|----------------|-----|---------------|
| Define invariantes formales | ✅ | ❌ |
| Exporta invariant manifest | ✅ | ❌ (consume) |
| Define taxonomía de errores HVL | ✅ | ❌ (usa) |
| Ejecuta inferencia causal | ❌ | ✅ |
| Implementa HVL | ❌ | ✅ |
| Evalúa calidad de evidencia | ❌ | ✅ |
| Calibra probabilidades | ❌ | ✅ |
| Detecta drift | ❌ | ✅ |
| Modifica pesos/reglas | ❌ Nunca | ❌ Nunca (HVL no corrige) |
| Emite anomalías formales | ✅ Códigos de error | ✅ HVLReport |

---

## Relación con AGENTS.md (marco regulatorio)

| Cambio GFL | Alimenta |
|-----------|---------|
| `HVL.md` con estados graduados | Risk Management File — clasificación de riesgo (§2) |
| `invariant_manifest.json` | Software Documentation — especificación formal (§5) |
| Deprecación PFUL/ERC | Technical File — justificación de decisiones de diseño (§5) |
| Taxonomía errores HVL | Software Documentation — trazabilidad de errores (§3.1) |
| Non-Intervention Principle | Human-in-the-loop definido (§3.2) |

---

## Orden de implementación recomendado

1. Crear `docs/deprecated/` con README de deprecación
2. Mover PFUL.md y ERC.md con banners NON-CANONICAL
3. Actualizar INVARIANT_BOUNDARIES.md (A2)
4. Actualizar CONSTITUTION.md (A3)
5. Crear HVL.md (A1) — requiere A2 y A3 como contexto
6. Expandir errors.py (A6)
7. Crear script `scripts/export_invariant_manifest.py` y generar `spec/invariant_manifest.json` (A5)
8. Notificar a GeneForge que el manifest está disponible

---

## Lo que NO cambia en este plan

- La conformance suite existente no se modifica
- Los invariantes del Immutable Core no cambian (solo se exportan)
- El proceso de GFL-RFC no cambia
- Ningún test existente debe romperse
- El validator.py semántico existente no se toca

---

*Este documento es un plan de revisión. No se implementa nada hasta aprobación de coordinadores de ambos repositorios.*
