# GFL API Contract Layer

## 1. Introduction
The **GFL API Contract Layer** formalizes the exact integration boundary between the GeneForgeLang (GFL) standard and downstream consumers, such as the GeneForge Execution Engine. It enforces structural decoupling by explicitly declaring which components of GFL are part of the public API and which are strictly internal.

## 2. The Golden Rule of Integration
> **Downstream systems MUST ONLY consume `geneforgelang.api` or explicitly versioned contracts.**

Any downstream system (including GeneForge) that imports internal GFL modules, models, or extensions is considered to be violating the dependency boundary and is structurally invalid.

## 3. Allowed Public API Surface

The following paths are explicitly exposed for downstream integration:

*   `geneforgelang.api`: The primary entry point for parsing, validation, and semantic interpretation.
*   `geneforgelang.contracts.*`: Versioned schemas, AST structures, and Epistemic Resolution Contract (ERC) definitions.
*   `geneforgelang.types.*`: Publicly exposed types and enumerations needed for interacting with the API (e.g., `GFLAST`, `ValidationResult`).

## 4. Prohibited Internal Implementations

The following paths are **STRICTLY PROHIBITED** from being imported by any external system. These are internal implementation details of the GFL core and are subject to change without notice:

*   `geneforgelang.models.*`: Internal models used for reasoning or parsing logic.
*   `geneforgelang.cli.*`: Command-line interface utilities.
*   `geneforgelang.extensions.*`: Extension implementations and experimental features.
*   `geneforgelang.utils.*`: Internal utility functions not intended for public use.
*   `geneforgelang.core.*` (excluding `geneforgelang.core.api` and exposed types): The core parser and validator implementations.

## 5. Enforcement
1. **Testing Boundaries**: Any test in a downstream repository that relies on a prohibited internal module is considered technical debt and must be removed or migrated to the GFL repository.
2. **CI Validation**: Future CI pipelines will enforce these boundaries using static analysis (e.g., import linting) to ensure that downstream repositories do not accidentally leak dependencies back into GFL.
3. **API Evolution**: Changes to the public API surface require a formal GFL-RFC.

## 6. Conclusion
By adhering to this API Contract, we ensure that GeneForge remains an independent executor of the GFL standard, capable of functioning alongside other conformant interpreters without being tightly coupled to GFL's internal mechanics.
