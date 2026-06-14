# RFC-002_UNKNOWN_TOOL

## Status: PROPOSED
**Auto-Generated based on Brutal Test Metrics**
**Recurrence Score**: 80/100 workflows

## Observation
During the execution of 100 synthetic real-world workflows from ClawBio, the validator flagged the `UNKNOWN_TOOL` error 80 times.
Because this crosses the threshold of 5, it is considered a **persistent gap** in the language abstractions rather than a workflow anomaly.

## Proposed Resolution
- If `UNKNOWN_TOOL` relates to enums (e.g., `UNKNOWN_EXPERIMENT_TYPE`, `UNKNOWN_STRATEGY`), the `gftypes.py` enums must be expanded.
- If `UNKNOWN_TOOL` relates to `UNKNOWN_TOOL`, the validator must defer tool validation to the `plugin_registry` rather than using a hardcoded list.

## Metric Validation
- **Total occurrences**: 80
- **Action Required**: Core Language Update
