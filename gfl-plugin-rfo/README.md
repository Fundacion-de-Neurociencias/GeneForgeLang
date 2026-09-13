# GFL Plugin: RFOptimization & Consensus Rescue

Plugin desacoplado y amputable (ADR-001 y ADR-0003) inspirado en el marco RFOptimization (DNA, research de David Baker Lab, bioRxiv 2026).

## Capacidades:
- **Clasificación de Frontera (NEAR_MISS)**: Detecta candidatos borderline para evitar su descarte innecesario.
- **Bucle de Rescate Alternante**: Optimización guiada por gradientes (differentiable heads) y rediseño discreto (ProteinMPON/LigandMPNN).
- **Consenso Multi-Modelo Screening**: Evita sobreajuste a un único predictor mediante filtros cruzados (Independent AF3: iPAE < 2.5, iPTM > 0.8, RF3 y Boltz1).
