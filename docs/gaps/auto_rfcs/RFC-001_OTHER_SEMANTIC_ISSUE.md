# RFC-001_OTHER_SEMANTIC_ISSUE

## Status: PROPOSED
**Auto-Generated based on Brutal Test Metrics**
**Recurrence Score**: 114/100 workflows

## Observation
During the execution of 100 synthetic real-world workflows from ClawBio, the validator flagged the `OTHER_SEMANTIC_ISSUE` error 114 times.
Because this crosses the threshold of 5, it is considered a **persistent gap** in the language abstractions rather than a workflow anomaly.

## Proposed Resolution
- If `OTHER_SEMANTIC_ISSUE` relates to enums (e.g., `UNKNOWN_EXPERIMENT_TYPE`, `UNKNOWN_STRATEGY`), the `gftypes.py` enums must be expanded.
- If `OTHER_SEMANTIC_ISSUE` relates to `UNKNOWN_TOOL`, the validator must defer tool validation to the `plugin_registry` rather than using a hardcoded list.

## Metric Validation
- **Total occurrences**: 114
- **Action Required**: Core Language Update
