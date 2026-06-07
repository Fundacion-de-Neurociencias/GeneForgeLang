from dataclasses import dataclass


@dataclass(frozen=True)
class ProjectionPolicy:
    ignored_keys: frozenset[str]
    case_insensitive_value_keys: frozenset[str]
    unordered_list_keys: frozenset[str]


DEFAULT_POLICY = ProjectionPolicy(
    ignored_keys=frozenset(
        {
            "__file__",
            "__line__",
            "__parser__",
            "__trace__",
            "_meta",
            "metadata",
            "normalization_path",
            "parser_fallback",
            "source_loc",
            "source_location",
            "span",
            "line_number",
            "column",
            "source_file",
            "parse_trace",
            "fallback_origin",
        }
    ),
    case_insensitive_value_keys=frozenset(
        {
            "entity",
            "gene",
            "model",
            "target",
            "target_gene",
            "tool",
            "type",
            "protein",
            "protein_identifier",  # Based on spec
        }
    ),
    unordered_list_keys=frozenset({"annotations", "constraints", "evidence", "params", "tags", "modifiers"}),
)


def filter_non_semantic_annotations(node: dict) -> None:
    """Annotation neutrality: removes non-semantic annotations like @comment."""
    if "annotations" in node and isinstance(node["annotations"], list):
        filtered = [
            ann for ann in node["annotations"] if isinstance(ann, dict) and ann.get("type", "").lower() != "comment"
        ]
        if filtered:
            node["annotations"] = filtered
        else:
            del node["annotations"]
