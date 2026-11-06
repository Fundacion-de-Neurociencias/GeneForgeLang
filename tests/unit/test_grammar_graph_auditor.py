"""Unit test suite for Graphify AST grammar auditing and GFL bridge scripts."""

from __future__ import annotations

import json
from pathlib import Path

from geneforgelang.core.grammar_graph import audit_grammar_graph, bridge_gfl_files_to_graph


class TestGrammarGraphAuditor:
    """Tests for the static knowledge graph grammar auditor."""

    def test_audit_grammar_synthetic_graph(self) -> None:
        synthetic_graph = {
            "directed": True,
            "multigraph": False,
            "nodes": [
                {
                    "id": "src_geneforgelang_core_gftypes_protokcontract",
                    "label": "ProTokContract",
                    "source_file": "src/geneforgelang/core/gftypes.py",
                    "source_location": "L3137",
                    "file_type": "code",
                },
                {
                    "id": "src_geneforgelang_core_gftypes_orphancontract",
                    "label": "OrphanContract",
                    "source_file": "src/geneforgelang/core/gftypes.py",
                    "source_location": "L9999",
                    "file_type": "code",
                },
                {
                    "id": "src_geneforgelang_core_validator_enhancedsemanticvalidator",
                    "label": "EnhancedSemanticValidator",
                    "source_file": "src/geneforgelang/core/validator.py",
                    "source_location": "L50",
                    "file_type": "code",
                },
                {
                    "id": "tests_unit_test_protok_testprotokengine",
                    "label": "TestProTokEngine",
                    "source_file": "tests/unit/test_protok.py",
                    "source_location": "L213",
                    "file_type": "code",
                },
            ],
            "links": [
                {
                    "source": "src_geneforgelang_core_gftypes_protokcontract",
                    "target": "src_geneforgelang_core_validator_enhancedsemanticvalidator",
                    "relation": "validated_by",
                },
                {
                    "source": "tests_unit_test_protok_testprotokengine",
                    "target": "src_geneforgelang_core_gftypes_protokcontract",
                    "relation": "tests",
                },
            ],
        }

        report = audit_grammar_graph(synthetic_graph)
        assert report["total_nodes"] == 4
        assert report["total_edges"] == 2

        contracts = {c["label"]: c for c in report["audited_contracts"]}
        assert "ProTokContract" in contracts
        assert contracts["ProTokContract"]["status"] == "PASSED"
        assert contracts["ProTokContract"]["has_validator_link"] is True
        assert contracts["ProTokContract"]["has_test_link"] is True

        assert "OrphanContract" in contracts
        assert contracts["OrphanContract"]["status"] == "ORPHAN"
        assert "OrphanContract" in report["orphan_contracts"]

    def test_bridge_gfl_files_to_graph(self, tmp_path: Path) -> None:
        # Create dummy repo layout
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()
        examples_dir = repo_dir / "examples"
        examples_dir.mkdir()

        sample_gfl = examples_dir / "sample_test.gfl"
        sample_gfl.write_text(
            """
experiment:
  tool: blast
  type: blastp
  params:
    sequence: MVKVGVNGF
protok:
  contract_id: enz_001
  modality: multimodal_residue_stream
  target_sequence: MVKVGVNGF
""",
            encoding="utf-8",
        )

        base_graph_path = tmp_path / "graph.json"
        base_graph = {
            "directed": True,
            "multigraph": False,
            "nodes": [
                {
                    "id": "src_geneforgelang_core_gftypes_protokcontract",
                    "label": "ProTokContract",
                    "file_type": "code",
                    "source_file": "src/geneforgelang/core/gftypes.py",
                },
                {
                    "id": "src_geneforgelang_core_gftypes_experiment",
                    "label": "Experiment",
                    "file_type": "code",
                    "source_file": "src/geneforgelang/core/gftypes.py",
                },
            ],
            "links": [],
        }
        base_graph_path.write_text(json.dumps(base_graph), encoding="utf-8")

        res = bridge_gfl_files_to_graph(
            repo_root=repo_dir,
            graph_path=base_graph_path,
            out_path=base_graph_path,
        )

        assert res["parsed_files"] == 1
        assert res["added_nodes"] == 3  # 1 file node + 2 block nodes (experiment, protok)
        assert res["added_links"] == 4  # 2 contains links + 2 instantiates_contract links

        # Verify saved content
        saved_data = json.loads(base_graph_path.read_text(encoding="utf-8"))
        node_ids = {n["id"] for n in saved_data["nodes"]}
        assert "gfl_examples_sample_test_gfl" in node_ids
        assert "gfl_examples_sample_test_gfl_block_protok" in node_ids
        assert "gfl_examples_sample_test_gfl_block_experiment" in node_ids
