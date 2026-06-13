import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.parent


def generate_rfcs():
    metrics_path = REPO_ROOT / "docs" / "gaps" / "brutal_test_metrics.json"
    rfc_dir = REPO_ROOT / "docs" / "gaps" / "auto_rfcs"
    rfc_dir.mkdir(parents=True, exist_ok=True)

    with open(metrics_path, encoding="utf-8") as f:
        metrics = json.load(f)

    gaps = metrics.get("recurrent_gaps", {})

    threshold = 5  # Persists in more than 5 workflows
    rfc_count = 0

    for gap_type, count in gaps.items():
        if count >= threshold:
            rfc_count += 1
            rfc_id = f"RFC-{str(rfc_count).zfill(3)}_{gap_type}"
            rfc_file = rfc_dir / f"{rfc_id}.md"

            content = f"""# {rfc_id}

## Status: PROPOSED
**Auto-Generated based on Brutal Test Metrics**
**Recurrence Score**: {count}/100 workflows

## Observation
During the execution of 100 synthetic real-world workflows from ClawBio, the validator flagged the `{gap_type}` error {count} times.
Because this crosses the threshold of {threshold}, it is considered a **persistent gap** in the language abstractions rather than a workflow anomaly.

## Proposed Resolution
- If `{gap_type}` relates to enums (e.g., `UNKNOWN_EXPERIMENT_TYPE`, `UNKNOWN_STRATEGY`), the `gftypes.py` enums must be expanded.
- If `{gap_type}` relates to `UNKNOWN_TOOL`, the validator must defer tool validation to the `plugin_registry` rather than using a hardcoded list.

## Metric Validation
- **Total occurrences**: {count}
- **Action Required**: Core Language Update
"""
            rfc_file.write_text(content, encoding="utf-8")
            print(f"Generated RFC: {rfc_file.name}")


if __name__ == "__main__":
    generate_rfcs()
