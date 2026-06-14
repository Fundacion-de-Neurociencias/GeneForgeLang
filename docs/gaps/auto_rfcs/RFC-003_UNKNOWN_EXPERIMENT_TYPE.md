# RFC-003_UNKNOWN_EXPERIMENT_TYPE

## Status: PROPOSED
**Auto-Generated based on Brutal Test Metrics**
**Recurrence Score**: 28/100 workflows

## Observation
During the execution of 100 synthetic real-world workflows from ClawBio, the validator flagged the `UNKNOWN_EXPERIMENT_TYPE` error 28 times.
Because this crosses the threshold of 5, it is considered a **persistent gap** in the language abstractions rather than a workflow anomaly.

## Proposed Resolution
- If `UNKNOWN_EXPERIMENT_TYPE` relates to enums (e.g., `UNKNOWN_EXPERIMENT_TYPE`, `UNKNOWN_STRATEGY`), the `gftypes.py` enums must be expanded.
- If `UNKNOWN_EXPERIMENT_TYPE` relates to `UNKNOWN_TOOL`, the validator must defer tool validation to the `plugin_registry` rather than using a hardcoded list.

## Metric Validation
- **Total occurrences**: 28
- **Action Required**: Core Language Update
