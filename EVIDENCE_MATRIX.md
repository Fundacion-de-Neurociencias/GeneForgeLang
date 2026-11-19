# Evidence Matrix (Neurodiagnoses Quality Standard)

> **Criterio de Calidad**: Ninguna variable entra en análisis, entrenamiento, validación o publicación mientras no exista trazabilidad completa entre definición clínica, diccionario oficial, unidad física, codificación de missing y transformación aplicada.

Ninguna variable pasará a estado `VERIFIED` hasta que todas las columnas de esta matriz estén respaldadas por documentación oficial explícita, no por inferencia lógica.

| Variable | Diccionario ADNI | Diccionario NACC | Unidad | Missing codes | Transformación autorizada | Estado |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **AGE** | *Pendiente doc* | *Pendiente doc* | Años | - | Ninguna | `OBSERVED` |
| **SEX** | *Pendiente doc* | *Pendiente doc* | Categórico | - | Mapeo binario | `OBSERVED` |
| **EDUCATION** | *Pendiente doc* | *Pendiente doc* | Años | ADNI: -1 (?), NACC: 99 | A `NaN` | `BLOCKED` |
| **APOE4** | *Pendiente doc* | *Pendiente doc* | Numérico/Categ. | NACC: 9 | Ninguna | `BLOCKED` |
| **MMSE** | *Pendiente doc* | UDS: -4, 88, 99 | Puntuación | NACC: -4, 88, 99 | A `NaN` | `BLOCKED` |
| **CDRSB** | *Pendiente doc* | *Pendiente doc* | Puntuación | NACC: 88, 99 | A `NaN` | `BLOCKED` |
| **HIPPOCAMPUS** | *Pendiente doc* | *Pendiente doc* | **Desconocida** | *Pendiente doc* | **Pausada** | `BLOCKED` |
| **ICV** | *Pendiente doc* | *Pendiente doc* | **Desconocida** | *Pendiente doc* | **Pausada** | `BLOCKED` |
| **DIAGNOSIS** | *Pendiente doc* | *Pendiente doc* | Categórico | NACC: 8 (Peligro) | **Pausada** | `BLOCKED` |
| **rtvFTD_KNOWLEDGE_LOSS** | Ulugut et al. (2025) | *Pendiente map* | Categórico | *Pendiente* | Mapeo a FTLD module | `DOCUMENTED` |
| **rtvFTD_EMPATHY_LOSS** | Ulugut et al. (2025) | *Pendiente map* | Categórico | *Pendiente* | Mapeo a FTLD module | `DOCUMENTED` |
| **rtvFTD_ASYM_RIGHT_TEMP** | Ulugut et al. (2025) | *Pendiente map* | Volumétrico | *Pendiente* | Cálculo de asimetría | `DOCUMENTED` |
| **PLASMA_GFAP** | Bellomo et al. (2026) | Bellomo et al. (2026) | Proteómica | *Pendiente* | Escalar | `DOCUMENTED` |
| **PLASMA_NfL** | Bellomo et al. (2026) | Bellomo et al. (2026) | Proteómica | *Pendiente* | Escalar | `DOCUMENTED` |
| **PLASMA_ITGAV** | Bellomo et al. (2026) | Bellomo et al. (2026) | Proteómica | *Pendiente* | Escalar | `DOCUMENTED` |
| **PLASMA_ITGAM** | Bellomo et al. (2026) | Bellomo et al. (2026) | Proteómica | *Pendiente* | Escalar | `DOCUMENTED` |
| **3D_COMPARTMENT_MIXING** | Zhang et al. (2026) | *Pendiente map* | Topológico (TAD) | *Pendiente* | Modificador weight_tier | `DOCUMENTED` |
| **3D_LOOP_DISRUPTION** | Zhang et al. (2026) | *Pendiente map* | Topológico (Loop) | *Pendiente* | Modificador weight_tier | `DOCUMENTED` |
| **GNOMAD_AF** | Broad Institute | *Pendiente map* | Frecuencia Alélica | *Pendiente* | Filtro prevalencia poblacional | `DOCUMENTED` |
| **ALPHAGENOME_QUANTILE** | DeepMind AlphaGenome | *Pendiente map* | Cuantil Regulador | *Pendiente* | Reclasificación riesgo epigenético | `DOCUMENTED` |
| **4D_NUCLEOME_CONTACTS** | ENCODE / 4D Nucleome | *Pendiente map* | Conteo (Lazos 3D) | *Pendiente* | Validación estructural causal | `DOCUMENTED` |

---

### Hallazgo H0 (Definitivo de la Jornada)

> **Antes de la auditoría ontológica no existe evidencia suficiente para interpretar el fracaso ADNI→NACC como un problema de generalización biológica.**

Todas las conclusiones previas (incluyendo la inferencia matemática de que el Hipocampo NACC estaba en $cm^3$ y que el diagnóstico `8` es un control sano directo) han sido degradadas a **hipótesis no verificadas**. El proyecto permanecerá en esta fase documental hasta que se localicen los manuales originales exactos.
