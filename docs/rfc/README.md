# GFL RFC (Request for Comments) Process

## 1. What is an RFC?
A GFL RFC (Request for Comments) is a formal proposal to modify the GeneForgeLang standard. This includes:
*   Changes to the core grammar.
*   New biological primitives or instruction sets.
*   Updates to the Biological State Space structure.
*   Formalization of new biological invariants.

The RFC process is designed to ensure that GFL evolves in a way that is scientifically sound, implementable, and backwards-compatible.

## 2. When is an RFC Required?
An RFC is required for any change that affects the **Semantics** or **Public Interface** of GFL. Minor documentation fixes or internal validator optimizations do not require an RFC.

## 3. RFC Lifecycle

### 3.1 Drafting (Draft)
The proposer creates a new file in `docs/rfc/` using the [RFC Template](rfc_template.md). The status is set to `DRAFT`.

### 3.2 Discussion (Proposed)
The proposer opens a Pull Request for the RFC. The GFL community (researchers, runtime developers, etc.) provides feedback on:
*   Scientific validity.
*   Causal consistency.
*   Cross-runtime portability.

### 3.3 Final Comment Period (FCP)
Once major concerns are addressed, the RFC enters a Final Comment Period. This is a last call for feedback before acceptance.

### 3.4 Acceptance (Accepted)
If the RFC is accepted, it is merged into the `main` branch. The status is updated to `ACCEPTED`.
The changes described in the RFC must then be implemented in the GFL validator and reflected in the formal specifications (`docs/spec/`).

### 3.5 Implementation (Implemented)
Once the code and specifications are updated, the RFC status is updated to `IMPLEMENTED` and assigned a GFL Version (e.g., `GFL v2.1.0`).

### 3.6 Rejection/Withdrawal (Rejected/Withdrawn)
RFCs that do not gain consensus or are withdrawn by the proposer are moved to the `archived/` section of the RFC repository.

## 4. RFC Template
All RFCs must use the standard [GFL RFC Template](rfc_template.md).

## 5. Participation
As an open standard, GFL welcomes RFCs from anyone in the scientific and engineering community.
