# GFL Plugin: RFOptimization & Consensus Rescue
 
Decoupled and amputatable plugin (ADR-001 & ADR-0003) inspired by the RFOptimization framework (David Baker Lab, bioRxiv 2026).
 
## Capabilities:
- **Borderline Classification (`NEAR_MISS`)**: Detects borderline candidates near decision boundaries to prevent discarding viable designs.
- **Alternating Rescue Loop**: Gradient-guided optimization via differentiable prediction heads combined with discrete sequence redesign (ProteinMPNN / LigandMPNN).
- **Multi-Model Consensus Screening**: Eliminates single-predictor bias through strict cross-model filters (Independent AlphaFold 3: $iPAE < 2.5, iPTM > 0.8$, RoseTTAFold 3, and Boltz-1).
