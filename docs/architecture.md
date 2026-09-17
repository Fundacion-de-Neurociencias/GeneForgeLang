# GeneForgeLang (GFL) Architecture Specification

> **The Symbolic Language & Semantic Constitution for Biological Reasoning and Multi-Omic Design**  
> *Versión Canónica: GFL v2.0+ (Ecosistema NeuroIA / Fundación de Neurociencias)*

---

## 1. Misión y Posición Constitucional

GeneForgeLang (GFL) es el **lenguaje formal de especificación y autoridad legislativa** para la representación del mundo biológico en el ecosistema NeuroIA:

$$\text{GFL} = \text{Constitución y Semántica} \quad\longleftrightarrow\quad \text{GeneForge} = \text{Ejecutivo y Runtime} \quad\longleftrightarrow\quad \text{CAL} = \text{Judicial y Arbitraje}$$

GFL define qué transformaciones biológicas son válidas, cuál es el espacio de estados canónico y qué contratos matemáticos, tensoriales y de gobernanza deben cumplirse para que un diseño o hipótesis sea admisible. GeneForge ejecuta e infiere sobre dicha realidad, pero **jamás puede mutar las reglas semánticas del lenguaje** (Invariante anti-colapso epistémico, `CONSTITUTION.md`).

---

## 2. Axiomas Bio-Semánticos Fundamentales

### 2.1. Axioma Bio-Termodinámico del Impuesto Metabólico
> *"El metabolismo es el impuesto termodinámico global que paga el organismo por su orden local."*

En GFL, ninguna síntesis estructural ni procesamiento informático ocurre sin disipación entrópica. Toda reducción local de entropía ($\Delta S_{\text{local}} < 0$) acarrea un costo metabólico explícito de primer orden integrado en las compuertas de parada y en los optimizadores.

### 2.2. Mandato de Gobernanza Genómica y Soberanía de Datos
La semántica biológica incluye dimensiones inseparables de gobernanza:
- **Provenance Scope**: Rastreo inmutable de linaje (`PUBLIC`, `CONTROLLED`, `CLINICAL`, `COMMERCIAL`, `RESTRICTED`).
- **Consent Scope**: Delimitación de uso ético (`RESEARCH_ONLY`, `CLINICAL_CARE`, `COMMERCIAL_USE`, `POPULATION_GENOMICS`).
- **Population Scope & Sensitivity**: Conciencia de estratificación poblacional, ancestral y etnias para prevenir sesgos y desequilibrios.
- **Data Sovereignty & Biosecurity**: Restricciones jurisdiccionales (`EU`, `US`, `LOCAL_ONLY`) y puntuación de bioseguridad ante patógenos/toxinas de uso dual.

### 2.3. Hipótesis del Refinamiento Epistémico (Representaciones como Priors)
En GFL, ningún candidato ni afirmación causal es un dogma absoluto. El estado representa una creencia previa $P(\text{Claim} \mid \mathcal{E}_{\text{prior}})$:
- **Evidencia No Destructiva**: La nueva evidencia experimental no sobreescribe ciegamente los grafos previos, sino que los particiona y refina.
- **Partición Contextual**: Si un hallazgo nuevo difiere según el tejido o cohorte, el lenguaje bifurca la equivalencia en sub-afirmaciones condicionales.
- **Autómata Finito de Creencia (Evidence DFA)**: Estados de validez: `SUPPORTED` $\to$ `CONTESTED` $\to$ `CONDITIONALLY_VALID` $\to$ `SUPERSEDED`.

---

## 3. Arquitectura del Sistema (Capas del Compilador y Runtime)

```
┌────────────────────────────────────────────────────────────────────────┐
│                        GFL Workflow / Script (.gfl)                    │
│      (experiment, analyze, design, optimize, rules, hypothesis)        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  CAPA 1: PARSER & AST BUILDER (src/geneforgelang/core/parser.py)       │
│  - Sintaxis declarativa YAML-compatible y DSL semántico                │
│  - Generación del AST canónico (GFLAST, Experiment, Analysis, Design)  │
│  - Inyección dinámica de variables e interpolación (${param})          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  CAPA 2: VALIDADOR SEMÁNTICO & CAPABILITY-AWARE GATES                  │
│  (src/geneforgelang/core/semantic_validator.py)                        │
│  - Chequeo estático de tipos y compatibilidad biológica                │
│  - Validación de entidades, ontologías (HGNC, GO, ChEBI, UniProt)      │
│  - Validación de Hipótesis Simbólicas (SEMANTIC009, SEMANTIC010)       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  CAPA 3: CONTRATOS DE E/S Y TENSORES GEOMÉTRICOS (BioTorch Contracts)  │
│  - IOContract (FASTQ, BAM, VCF, CSV, JSON, TENSOR, CUSTOM)             │
│  - TensorContract: shapes estandarizados, invariant_dimensions,        │
│    coordinate_frames (SE(3), SO(3), local_residue_frame)               │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  CAPA 4: MOTOR DE GRAFOS CAUSALES Y TOPOLOGÍA                          │
│  - CausalTransitionNode: PHENOTYPIC -> CELLULAR -> MOLECULAR -> ATOMIC │
│  - Transiciones causales con scores de evidencia y dependencias CRISPR │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  CAPA 5: ECOSISTEMA DE PLUGINS AMPUTABLES (ADR-001 / ADR-0003)         │
│  Descubrimiento dinámico mediante Python Entry-Points                  │
│                                                                        │
│  ├── ClawBio Plugin (Stress testing biológico y resiliencia)           │
│  ├── AlphaGenome Atlas Plugin (AVI Score 18 modalidades, TF-MoDISco)   │
│  ├── DepMap CRISPR Plugin (Co-dependencias funcionales y stop-gates)   │
│  └── RFOptimization Plugin (Rescate de Near-Miss y Consenso AF3/RF3)   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Estructura de Tipos Canónicos (`src/geneforgelang/core/gftypes.py`)

GFL Core centraliza todos los contratos de datos en estructuras inmutables y serializables:

1. **Tipos de Datos y Biosecuencias**:
   - `DataType`: `FASTA`, `FASTQ`, `BAM`, `SAM`, `VCF`, `TENSOR`, `DISTANCE_MATRIX`, `BACKBONE_FRAMES`, `CONTACT_MAP`, `SEQUENCE_EMBEDDING`, `ATTENTION_MAP`.
   - `IOContract`: Valida contratos de entrada y salida entre bloques con chequeo estático previo a ejecución.
   - `TensorContract`: Define geometría y restricciones invariantes para modelos tensoriales de biología estructural.

2. **Estructuras Causales y Epistémicas**:
   - `CausalLevel`: Niveles de abstracción biológica (`PHENOTYPIC`, `CELLULAR`, `MOLECULAR`, `ATOMIC`).
   - `CausalTransitionNode`: Nodo formal en un grafo causal multiescala con fuentes de evidencia inmutables.
   - `CoDependencyTier`: Estratificación de dependencia funcional CRISPR (`HIGH`, `MODERATE`, `WEAK`, `NONE`).
   - `DepMapCoDependency`: Representación canónica de cribado CRISPR DepMap Public con compuerta de parada (`is_significant`).

3. **Ciclo de Vida de Candidatos y Optimización de Frontera (RFOptimization)**:
   - `CandidateStatus`: `VALIDATED`, `NEAR_MISS`, `REJECTED`, `OPTIMIZED`.
   - `ConsensusModel`: `AF3`, `RF3`, `BOLTZ`, `PROTEIN_MPNN`, `LIGAND_MPNN`.
   - `MultiModelConsensus`: Criterio tri-modelo independiente ($iPAE < 2.5, iPTM > 0.8$, confianzas mínimas) para blindar los diseños frente a sobreajustes de un solo predictor.
   - `RescuePolicy`: Define márgenes de frontera (`near_miss_margin`), ciclos de mutación guiada por gradientes y rediseño discreto.

4. **Integración con Modelos Fundacionales Genómicos (AlphaGenome)**:
   - `AviModality`: 18 canales aditivos de impacto funcional (Splicing, AlphaMissense, ChIP-TF, DNASE, etc.).
   - `AviScore`: Puntuación unificada de impacto molecular para 9 mil millones de SNVs codificantes y no codificantes.
   - `RegulatoryMotifAnnotation`: Disrupción de motivos regulatorios predichos con TF-MoDISco-lite.

---

## 5. El Ecosistema de Plugins Amputables (Decoupled Plugins)

De acuerdo con **ADR-001** y **ADR-0003**:
- El núcleo ligero de GFL (`geneforgelang-core`) no incluye frameworks pesados de deep learning (PyTorch, TensorFlow, JAX, RoseTTAFold, Boltz).
- Los plugins se distribuyen como paquetes satélite autónomos con su propio `pyproject.toml` y se conectan mediante `entry-points` en el grupo `geneforgelang.plugins`:

```toml
[project.entry-points."geneforgelang.plugins"]
alphagenome = "gfl_plugin_alphagenome.plugin:AlphaGenomePlugin"
depmap = "gfl_plugin_depmap.plugin:DepMapPlugin"
rfo = "gfl_plugin_rfo.plugin:RFOptimizationPlugin"
clawbio = "gfl_plugin_clawbio.plugin:ClawBioPlugin"
```

### Principios de Aislamiento y Resiliencia
1. **Amputabilidad Total**: La desinstalación de cualquier plugin no rompe el parser ni la validación semántica de GFL.
2. **Fallback Elegante**: Si un plugin no está instalado en el entorno, el validador emite una advertencia o sugiere el contenedor correspondiente sin crashear.
3. **Cero Mocks en Publicación**: En entornos productivos y de validación científica, las llamadas consultan APIs reales o datasets locales certificados, respetando la política de rigor científico.

---

## 6. Flujo de Desarrollo, Testing y CI/CD (Protocolo `/neuroia`)

1. **Aislamiento en Ramas**: Todos los desarrollos sustanciales se implementan en ramas temáticas (`feature/...`, `feat/...`), jamás directamente sobre `main`.
2. **Compromisos Atómicos**: Mensajes convencionales estructurados (`feat:`, `fix:`, `refactor:`, `docs:`).
3. **Compuerta de Verificación Exhaustiva**:
   ```powershell
   # Tests específicos del plugin o feature
   pytest tests/test_<feature>.py -v
   # Suite de regresión global
   pytest tests/unit/ -q
   ```
4. **Pull Request Obligatorio**: Apertura formal de PR con título y descripción detallada hacia `main`.
5. **Documentación Automática Continua**: Toda adición de tipos, plugins o directivas sintácticas debe reflejarse inmediatamente en `docs/architecture.md`, `docs/index.md`, `docs/geneforgelang/plugins/PLUGIN_ECOSYSTEM.md` y `CHANGELOG.md`.

