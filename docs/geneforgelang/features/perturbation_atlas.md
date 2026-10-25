# Perturbation Atlas & Distributed Biological Reasoning (`perturbation_atlas`)

The `perturbation_atlas` contract in GeneForgeLang (GFL) formalizes **Distributed Biological Reasoning** for high-throughput single-cell perturbation screens. Grounded in landmark discoveries by OpenAI, Scripps Research (Jin Lab), and PerturbAI (*Sun et al., 2026, bioRxiv; Shi et al., 2026, bioRxiv*), this block enables researchers and AI swarms to analyze complex perturbation atlases (such as the 7.7-million-cell mouse whole-brain in vivo Perturb-seq atlas) through parallelized, autonomous agents.

---

## 1. Scientific Background & The Reasoning Atlas Paradigm

### The High-Throughput Bottleneck
Traditional functional genomics screens interrogate thousands of genetic perturbations simultaneously across hundreds of cell types. In the whole-brain Perturb-seq atlas by Shi et al. (2026), 1,947 disease genes were disrupted in vivo across 7.7 million cells. Manually examining differential expression, cell-type specificity, and literature grounding for 1,947 genes takes human teams between several months and a year.

### Distributed Biological Reasoning vs. Monolithic LLMs
In benchmarks by Sun et al. (2026), monolithic single-agent LLMs collapse or hallucinate when processing whole atlases due to context dilution. The distributed framework decomposes analysis into **unary agent allocations**:
- **1 Agent per Perturbation**: Each autonomous agent interrogates differential expression for a single gene, pulls relevant scientific literature (via PubMed, Semantic Scholar), and synthesizes structured findings.
- **$\times 100$ Literature Coverage**: Unary agents retrieve orders of magnitude more relevant citations than single-agent approaches.
- **75% Human Expert Preference**: Blinded evaluators consistently favored distributed agent outputs over monolithic summaries.
- **Synthesis into a Reasoning Atlas**: Individual findings are aggregated into a global epistemic graph mapping cellular phenotypes, causal transitions, and phenotypic opposition between gene paralogs.

---

## 2. Key Biophysical & Epistemic Capabilities in GFL

1. **Paralog Phenotypic Dissonance (`divergence_check`)**:
   - Sequences with high structural homology often drive fundamentally divergent or opposing transcriptional programs in native neural tissue (e.g., NMDA receptor subunits *Grin2a* vs *Grin2b*, or mTOR regulators *Tsc1* vs *Tsc2*).
   - GFL enforces formal contracts evaluating paralog opposition with negative cosine similarity thresholds, preventing erroneous assumptions of functional equivalence.
2. **`ReasoningAtlasCompiler`**:
   - Compiles declarative GFL protocols into a formal `ReasoningAtlasGraph` containing:
     - **Nodes**: Perturbation target genes.
     - **Edges**: `SYNERGISTIC`, `OPPOSING`, `NEUTRAL`, or `DIVERGENT` relationships.
     - **Causal Transitions**: Automatic generation of `CausalTransitionNode` instances.
     - **Virtual Cell Coupling**: Generation of `VirtualCellPerturbationContract` instances for in silico simulation.
3. **Model Context Protocol (MCP) Bindings**:
   - Connects directly to remote MCP servers (e.g. `bioagents_shi` at `https://sites-publish-check-20261021.as-alexander-sun.chatgpt.site/api/shi-mcp`), allowing agents to query claims, related targets, and evidence paths without downloading multi-gigabyte raw datasets.

---

## 3. Declarative GFL Syntax

The `perturbation_atlas` (or `perturb_swarm`) block is declared with strict 2-space indentation:

```yaml
perturbation_atlas:
  name: "whole_brain_crispr_screen"
  organism: "Mus musculus"
  dataset_ref: "doi:10.64898/2026.10.15.759436v1"
  cell_atlas_size: 7700000
  modality: "in_vivo_perturb_seq"
  perturbation_targets:
    - gene: "DCTN1"
      pathway_focus: "cholesterol_metabolism"
      target_cell_types:
        - "cortical_neuron"
        - "striatal_medium_spiny_neuron"
      expected_phenotype: "retrograde_transport_and_cholesterol_clearance_defect"
      causal_transition_refs:
        - "CAUSAL_NEURODEGEN_LIPID_ACCUMULATION"
    - gene: "GRIN2A"
      pathway_focus: "nmda_glutamate_signaling"
      target_cell_types:
        - "cortical_pyramidal_neuron"
        - "hippocampal_ca1"
    - gene: "GRIN2B"
      pathway_focus: "nmda_glutamate_signaling"
      target_cell_types:
        - "cortical_pyramidal_neuron"
        - "hippocampal_ca1"
  swarm_policy:
    agent_granularity: "per_perturbation"
    literature_grounding: true
    min_expert_preference_score: 0.75
    synthesis_aggregator: "reasoning_atlas"
  divergence_check:
    evaluate_paralog_opposition: true
    pair:
      - "GRIN2A"
      - "GRIN2B"
    min_transcriptional_divergence: 0.35
  mcp_endpoint: "https://sites-publish-check-20261021.as-alexander-sun.chatgpt.site/api/shi-mcp"
  virtual_cell_link: "sim_vc_dctn1_cortical"

virtual_cell:
  simulation_id: "sim_vc_dctn1_cortical"
  cell_type: "cortical_neuron"
  target_gene_or_compound: "DCTN1"
  perturbation_type: "crispr_knockout"
  atlas_ref: "shi_brain_perturb_seq"
  dose_or_fold_change: 0.0
  readout:
    max_transcriptome_cosine_distance: 0.18
    min_survival_probability: 0.82
    mitochondrial_potential_retention: 0.89
    off_target_pathway_disruption: 0.05
  engine: "distributed-agent-virtual-cell"
  wet_lab_clearance: true
  tissue_context: "Whole-brain in vivo Perturb-seq atlas"
```

---

## 4. Python API & Compiler Usage

```python
import yaml
from geneforgelang.core.reasoning_atlas import ReasoningAtlasCompiler
from geneforgelang.core.validator import EnhancedSemanticValidator

# 1. Parse and validate GFL protocol
with open("examples/whole_brain_perturbation_reasoning_atlas.gfl", "r") as f:
    ast = yaml.safe_load(f)

validator = EnhancedSemanticValidator()
result = validator.validate_ast(ast)
assert result.is_valid

# 2. Compile into an epistemic ReasoningAtlasGraph
compiler = ReasoningAtlasCompiler(ast["perturbation_atlas"])
graph = compiler.compile()

print(f"Compiled Atlas: {graph.atlas_name} with {len(graph.nodes)} nodes and {len(graph.edges)} edges")

# Inspect confirmed paralog oppositions
for div in graph.paralog_divergences:
    print(f"Paralog divergence: {div['pair']} -> {div['status']}")

# 3. Export to causal transition nodes
causal_nodes = compiler.to_causal_nodes()
for node in causal_nodes:
    print(f"Causal node: {node.node_id} ({node.entity_name}) -> {node.biological_state}")

# 4. Generate grounded virtual cell simulation contract
vc_contract = compiler.to_virtual_cell_contract("DCTN1")
print(f"Virtual cell simulation: {vc_contract.simulation_id} on {vc_contract.cell_type}")
```

---

## 5. Citations & Attribution

- **Perturb-seq Dataset**: Shi, T., Korshunova, M., Kim, S., Jin, X. et al. *Genome-scale functional mapping of the mammalian whole brain with in vivo Perturb-seq*. bioRxiv (2026).
- **Distributed Agent Framework**: Sun, A. et al. *Distributed AI agents enable comprehensive discovery of biological insights at scale*. bioRxiv (2026). DOI: [10.64898/2026.10.15.759436v1](https://doi.org/10.64898/2026.10.15.759436v1).
- **Code Repository**: [`jinlabneurogenomics/distributed_agent`](https://github.com/jinlabneurogenomics/distributed_agent).
