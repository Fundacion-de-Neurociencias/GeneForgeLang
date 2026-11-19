# Merge Request: GWAS Empirical Rescue (Axis 1 + 2 + 3)

## Descripción
Este MR introduce la integración end-to-end empírica del orquestador de Neurodiagnoses para evaluar Variantes de Significado Incierto (VUS) asociadas al Alzheimer desde ClinVar.

El pipeline cruza datos de tres fuentes biológicas (sin simulación):
1. **gnomAD (Eje 1):** Frecuencia alélica (GraphQL nativo).
2. **AlphaGenome (Eje 2):** Impacto epigenético (quantiles de puntuaciones diferenciales de *foundation models* de DeepMind).
3. **4D Nucleome/ENCODE (Eje 3):** Conteo topológico de lazos 3D a través del microservicio FastAPI (`cooler` sobre HDF5 humano completo).

## Axis Mapping Compliance
- **Eje 1 (Etiología):** Capturado a través de ClinVar (VUS) y filtrado por frecuencia alélica extremadamente rara (gnomAD).
- **Eje 2 (Fisiopatología/Epigenómica):** El *foundation model* estima disrupción reguladora masiva, sugiriendo mecanismos fisiopatológicos no codificantes.
- **Eje 3 (Fenotipo/Neuroanatomía Celular):** Validación estructural empírica mediante la interrupción de lazos (loops) en la topología cromatínica de ENCODE/4D Nucleome.

## Cumplimiento de /neuroia (2-Layer System)
Este componente opera en **LAYER 2 — RESEARCH SYSTEM** como un experimento `offline` para validar la hipótesis causal estructural (Topología + Epigenómica) sobre variantes VUS. Los resultados son propuestos al `runtime system` (WebApp) a través de un endpoint API desacoplado. Ningún dato PII real ni sintético es utilizado; se operan exclusivamente datos abiertos empíricos de NCBI, Broad Institute, y ENCODE.

## Checklist Pre-Commit
- [x] `.gitignore` verificado (no se suben matrices HDF5 masivas).
- [x] Sin simuladores o mocks en inferencia de API (AlphaGenome real).
- [x] Documentación de Axis Mapping completada.
- [x] Alineación estricta con Neurodiagnoses Orquestador.
