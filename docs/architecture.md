# Architecture Overview

GeneForgeLang (GFL) follows a modular architecture designed for extensibility and performance in genomic workflows.

## Core Components

### 1. Parser & Validator
- Located in `src/geneforgelang/core/`.
- Responsibility: Translate GFL syntax (YAML-based) into an Abstract Syntax Tree (AST) and perform semantic validation against biological rules.

### 2. Execution Engine
- Responsibility: Orchestrate the execution of workflow blocks (`experiment`, `analyze`, `simulate`).
- Supports local execution and container-based execution for reproducibility.

### 3. Plugin System
- Located in `src/geneforgelang/plugins/`.
- Responsibility: Dynamic discovery and registration of biological tools (e.g., Blast, Samtools, GATK).

### 4. API & CLI
- CLI: `src/geneforgelang/cli/`.
- API: `src/geneforgelang/api/`.
- Responsibility: Provide user interfaces for interacting with the GFL engine.

## Data Flow
1. User provides `.gfl` file.
2. Parser generates AST.
3. Validator checks AST for structural and biological consistency.
4. Core Engine executes blocks sequentially or in parallel.
5. Results are generated and optionally saved to `results/`.
