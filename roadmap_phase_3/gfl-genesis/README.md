# GFL Genesis Project

## Optimización de ARN Guía (gRNA) para la Edición Genómica de TP53 mediante Descubrimiento Guiado por IA con GeneForgeLang

This project will use the `guided_discovery` block of GFL v1.0.0 to design a set of candidate guide RNA (gRNA) sequences for the human tumor suppressor gene TP53. The goal is to find gRNAs that maximize on-target cutting efficiency while simultaneously minimizing potential off-target cuts throughout the genome. The project will serve as scientific validation of the GFL language, generate a reference use case, and produce an open-source set of plugins for CRISPR design.

## Scientific Justification

CRISPR-Cas9 technology has revolutionized genetic engineering. However, its clinical success critically depends on the quality of the gRNA used. A suboptimal design can result in low editing efficiency or dangerous off-target mutagenic effects. Searching for optimal gRNAs is a combinatorial optimization problem in a massive search space, making it an ideal use case for the iterative design and evaluation cycle orchestrated by GFL's `guided_discovery` block.

## Objectives

### Primary
Demonstrate that the GFL workflow can identify gRNAs for TP53 with predicted on-target/off-target scores superior to those obtained by a simple exhaustive search.

### Secondary
- Validate the practical use of the GFL ecosystem (language, contracts, schemas, plugins) in a realistic research problem.
- Develop and publish at least two GFL plugins for CRISPR prediction tools.
- Generate the data and results for a preprint (bioRxiv) and a project blog post.

## Project Structure

```
gfl-genesis/
├── README.md
├── genesis.gfl
├── schemas/
│   └── crispr_types.yml
├── plugins/
│   ├── gfl-plugin-ontarget-scorer/
│   ├── gfl-plugin-offtarget-scorer/
│   └── gfl-crispr-evaluator/
├── data/
│   ├── genome/
│   └── annotations/
├── results/
└── docs/
```
