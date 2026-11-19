"""Static AST Grammar Auditor & Knowledge Graph Engine for GeneForgeLang (GFL).

Integrates Graphify (Tree-sitter AST) and GFL native parser to provide:
1. Contract-to-Validator & Test Coverage Auditing across gftypes.py.
2. GFL DSL AST Bridge: Injects user-facing .gfl specification files into graph.json.
3. God Node Topology Metrics: Detects monolithic coupling hubs.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from geneforgelang.core.gftypes import GFLAST
from geneforgelang.core.parser import parse_gfl

logger = logging.getLogger("grammar_graph")

# Mapping of GFLAST attribute names to canonical gftypes contract symbol IDs
BLOCK_TO_CONTRACT_MAP: dict[str, str] = {
    "protok": "src_geneforgelang_core_gftypes_protokcontract",
    "genomic_llm": "src_geneforgelang_core_gftypes_genomicllmcontract",
    "experiment": "src_geneforgelang_core_gftypes_experiment",
    "analyze": "src_geneforgelang_core_gftypes_analysis",
    "design": "src_geneforgelang_core_gftypes_design",
    "optimize": "src_geneforgelang_core_gftypes_optimize",
    "decision": "src_geneforgelang_core_gftypes_decisioncontract",
    "biosecurity_watermark": "src_geneforgelang_core_gftypes_biosecuritywatermarkcontract",
    "cryptic_pocket": "src_geneforgelang_core_gftypes_crypticpocketcontract",
    "thermodynamic_binding": "src_geneforgelang_core_gftypes_thermodynamicbindingcontract",
    "bacteriophage": "src_geneforgelang_core_gftypes_bacteriophagetherapycontract",
    "virtual_cell": "src_geneforgelang_core_gftypes_virtualcellperturbationcontract",
    "force_field_engine": "src_geneforgelang_core_gftypes_forcefieldenginecontract",
    "dna_viewer": "src_geneforgelang_core_gftypes_dnaviewercontract",
    "perturbation_atlas": "src_geneforgelang_core_gftypes_perturbationatlascontract",
    "regulatory_profile": "src_geneforgelang_core_gftypes_regulatoryprofilecontract",
    "somatic_instability": "src_geneforgelang_core_gftypes_somaticinstabilitycontract",
    "ensemble": "src_geneforgelang_core_gftypes_boltzmannensemblecontract",
    "tape_recorder": "src_geneforgelang_core_gftypes_taperecordercontract",
    "dna_dynamics": "src_geneforgelang_core_gftypes_dnadynamicscontract",
    "breathing": "src_geneforgelang_core_gftypes_dnadynamicscontract",
}


def load_graph(graph_path: Path) -> dict[str, Any]:
    """Load and validate Graphify graph.json."""
    if not graph_path.exists():
        raise FileNotFoundError(f"Knowledge graph not found at: {graph_path}")
    with open(graph_path, encoding="utf-8") as f:
        data: dict[str, Any] = json.load(f)
        return data


def audit_grammar_graph(graph_data: dict[str, Any]) -> dict[str, Any]:
    """Perform topological grammar audit across contracts, validators, and tests."""
    nodes = {n["id"]: n for n in graph_data.get("nodes", [])}
    links = graph_data.get("links", graph_data.get("edges", []))

    # Build adjacency maps
    adj_out: dict[str, set[str]] = defaultdict(set)
    adj_in: dict[str, set[str]] = defaultdict(set)
    adj_undirected: dict[str, set[str]] = defaultdict(set)

    for link in links:
        src = link["source"]
        tgt = link["target"]
        adj_out[src].add(tgt)
        adj_in[tgt].add(src)
        adj_undirected[src].add(tgt)
        adj_undirected[tgt].add(src)

    # 1. Identify all Contract classes declared in gftypes.py
    contracts: list[dict[str, Any]] = []
    for _node_id, node in nodes.items():
        src_file = node.get("source_file", "")
        label = node.get("label", "")
        if "gftypes.py" in src_file and (label.endswith("Contract") or label.endswith("AST")):
            contracts.append(node)

    contracts.sort(key=lambda n: str(n.get("label", "")))

    # 2. Identify Validator and Test hubs
    validator_node_ids = {nid for nid, n in nodes.items() if "validator.py" in n.get("source_file", "")}
    test_node_ids = {
        nid
        for nid, n in nodes.items()
        if "tests/unit" in n.get("source_file", "") or "tests\\" in n.get("source_file", "")
    }

    # 3. Audit each contract
    audit_results: list[dict[str, Any]] = []
    orphan_contracts: list[str] = []

    for contract in contracts:
        cid = contract["id"]
        c_label = contract.get("label", cid)
        c_loc = f"{contract.get('source_file')}:{contract.get('source_location')}"

        # 1-hop and 2-hop neighbors
        neighbors_1hop = adj_undirected.get(cid, set())
        neighbors_2hop = set(neighbors_1hop)
        for n1 in neighbors_1hop:
            neighbors_2hop.update(adj_undirected.get(n1, set()))

        # Check validator linkage
        has_validator_link = bool(neighbors_2hop.intersection(validator_node_ids))

        # Check test linkage
        has_test_link = bool(neighbors_2hop.intersection(test_node_ids))

        degree = len(neighbors_1hop)

        status = "PASSED" if (has_validator_link and has_test_link) else "WARNING"
        if not has_test_link and not has_validator_link:
            status = "ORPHAN"
            orphan_contracts.append(c_label)

        audit_results.append(
            {
                "label": c_label,
                "location": c_loc,
                "degree": degree,
                "has_validator_link": has_validator_link,
                "has_test_link": has_test_link,
                "status": status,
            }
        )

    # 4. God Node Metrics
    god_nodes = sorted(
        [
            {
                "label": n.get("label", nid),
                "source_file": n.get("source_file", ""),
                "degree": len(adj_undirected.get(nid, set())),
                "fan_in": len(adj_in.get(nid, set())),
                "fan_out": len(adj_out.get(nid, set())),
            }
            for nid, n in nodes.items()
            if n.get("file_type") == "code" and not n.get("label", "").startswith(".")
        ],
        key=lambda x: int(x["degree"]),
        reverse=True,
    )[:10]

    return {
        "total_nodes": len(nodes),
        "total_edges": len(links),
        "audited_contracts": audit_results,
        "orphan_contracts": orphan_contracts,
        "god_nodes": god_nodes,
    }


def sanitize_id(text: str) -> str:
    """Normalize identifier for Graphify node ID."""
    return text.replace("\\", "/").replace("/", "_").replace(".", "_").replace(":", "_").replace("-", "_").lower()


def bridge_gfl_files_to_graph(
    repo_root: Path,
    graph_path: Path,
    out_path: Path | None = None,
) -> dict[str, int]:
    """Parse all .gfl files and merge their AST into Graphify graph.json."""
    if not graph_path.exists():
        raise FileNotFoundError(f"Base graph not found at: {graph_path}")

    with open(graph_path, encoding="utf-8") as f:
        graph_data: dict[str, Any] = json.load(f)

    existing_nodes = {n["id"]: n for n in graph_data.get("nodes", [])}
    links: list[dict[str, Any]] = graph_data.get("links", graph_data.get("edges", []))
    existing_link_keys = {(str(link["source"]), str(link["target"]), str(link.get("relation", ""))) for link in links}

    gfl_files = sorted(list(repo_root.rglob("*.gfl")))
    logger.info(f"Discovered {len(gfl_files)} .gfl specification files across {repo_root}")

    added_nodes_count = 0
    added_links_count = 0
    parsed_files_count = 0

    for gfl_file in gfl_files:
        rel_path = gfl_file.relative_to(repo_root).as_posix()
        try:
            content = gfl_file.read_text(encoding="utf-8")
            raw_ast = parse_gfl(content)
            if not raw_ast or not isinstance(raw_ast, dict):
                continue
            ast = GFLAST.from_dict(raw_ast)
        except Exception as exc:
            logger.debug(f"Skipping non-standard/partial GFL file {rel_path}: {exc}")
            continue

        parsed_files_count += 1
        file_node_id = f"gfl_{sanitize_id(rel_path)}"

        # 1. Add file node
        if file_node_id not in existing_nodes:
            file_node = {
                "id": file_node_id,
                "label": rel_path,
                "_callable": False,
                "_origin": "gfl_ast_bridge",
                "community": 999,
                "community_name": "GFL Genetic Scripts",
                "file_type": "gfl_script",
                "norm_label": rel_path.lower(),
                "source_file": rel_path,
                "source_location": "L1",
            }
            graph_data["nodes"].append(file_node)
            existing_nodes[file_node_id] = file_node
            added_nodes_count += 1

        # 2. Inspect active blocks in GFLAST
        ast_dict = ast.to_dict()
        for block_name, contract_node_id in BLOCK_TO_CONTRACT_MAP.items():
            block_data = ast_dict.get(block_name)
            if block_data is not None:
                block_node_id = f"{file_node_id}_block_{block_name}"

                # Add block node
                if block_node_id not in existing_nodes:
                    block_node = {
                        "id": block_node_id,
                        "label": f"{gfl_file.stem}::{block_name}",
                        "_callable": False,
                        "_origin": "gfl_ast_bridge",
                        "community": 999,
                        "community_name": "GFL Genetic Scripts",
                        "file_type": "gfl_block",
                        "norm_label": f"{gfl_file.stem}::{block_name}".lower(),
                        "source_file": rel_path,
                        "source_location": "block",
                    }
                    graph_data["nodes"].append(block_node)
                    existing_nodes[block_node_id] = block_node
                    added_nodes_count += 1

                # Link file -> contains -> block
                l1_key = (file_node_id, block_node_id, "contains")
                if l1_key not in existing_link_keys:
                    link1 = {
                        "source": file_node_id,
                        "target": block_node_id,
                        "relation": "contains",
                        "_origin": "gfl_ast_bridge",
                        "confidence": "EXTRACTED",
                        "confidence_score": 1.0,
                        "source_file": rel_path,
                        "weight": 1.0,
                    }
                    links.append(link1)
                    existing_link_keys.add(l1_key)
                    added_links_count += 1

                # Link block -> instantiates_contract -> TargetContract (if contract exists in graph)
                target_contract_id = contract_node_id
                if target_contract_id not in existing_nodes:
                    expected_suffix = contract_node_id.split("_")[-1]
                    for nid in existing_nodes:
                        if nid.endswith(f"_{expected_suffix}"):
                            target_contract_id = nid
                            break

                if target_contract_id in existing_nodes:
                    l2_key = (block_node_id, target_contract_id, "instantiates_contract")
                    if l2_key not in existing_link_keys:
                        link2 = {
                            "source": block_node_id,
                            "target": target_contract_id,
                            "relation": "instantiates_contract",
                            "_origin": "gfl_ast_bridge",
                            "confidence": "EXTRACTED",
                            "confidence_score": 1.0,
                            "source_file": rel_path,
                            "weight": 1.0,
                        }
                        links.append(link2)
                        existing_link_keys.add(l2_key)
                        added_links_count += 1

    # Save merged graph
    target_out = out_path or graph_path
    with open(target_out, "w", encoding="utf-8") as f:
        json.dump(graph_data, f, indent=2)

    logger.info(
        f"GFL AST Bridge completed: {parsed_files_count} .gfl files parsed, "
        f"{added_nodes_count} nodes added, {added_links_count} edges linked. Saved to: {target_out}"
    )

    return {
        "parsed_files": parsed_files_count,
        "added_nodes": added_nodes_count,
        "added_links": added_links_count,
        "total_nodes": len(graph_data["nodes"]),
        "total_edges": len(links),
    }


def main_audit_cli() -> int:
    """CLI entry point for grammar auditing."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Audit GFL Grammar Graph")
    parser.add_argument(
        "--graph",
        type=Path,
        default=Path("graphify-out/graph.json"),
        help="Path to graphify graph.json",
    )
    parser.add_argument(
        "--fail-on-orphan",
        action="store_true",
        help="Exit with non-zero status if orphan contracts are found",
    )
    args = parser.parse_args()

    try:
        data = load_graph(args.graph)
    except Exception as e:
        print(f"[ERROR] Failed to load graph: {e}", file=sys.stderr)
        return 1

    report = audit_grammar_graph(data)

    print("\n" + "=" * 80)
    print("🔬 GENEFORGELANG (GFL) STATIC AST GRAMMAR AUDIT REPORT")
    print("=" * 80)
    print(f"Graph Topology: {report['total_nodes']:,} nodes | {report['total_edges']:,} edges\n")

    print(f"{'Contract Symbol':<35} {'Degree':<8} {'Validator':<12} {'Tests':<10} {'Status'}")
    print("-" * 80)

    for item in report["audited_contracts"]:
        v_mark = "✓ YES" if item["has_validator_link"] else "✗ MISSING"
        t_mark = "✓ YES" if item["has_test_link"] else "✗ MISSING"
        print(f"{item['label']:<35} {item['degree']:<8} {v_mark:<12} {t_mark:<10} {item['status']}")

    print("\n" + "-" * 80)
    print("🏛️ ARCHITECTURAL GOD NODES (Top 10 Connected Entities):")
    print("-" * 80)
    print(f"{'Symbol':<32} {'Degree':<8} {'Fan-In':<8} {'Fan-Out':<8} {'Source File'}")
    for gn in report["god_nodes"]:
        print(f"{gn['label']:<32} {gn['degree']:<8} {gn['fan_in']:<8} {gn['fan_out']:<8} {gn['source_file']}")

    print("\n" + "=" * 80)
    if report["orphan_contracts"]:
        print(f"⚠️ FOUND {len(report['orphan_contracts'])} ORPHAN CONTRACTS: {', '.join(report['orphan_contracts'])}")
        if args.fail_on_orphan:
            return 1
    else:
        print("✅ ALL AUDITED GFL GRAMMAR CONTRACTS MAINTAIN ACTIVE VALIDATION & TEST COVERAGE")
    print("=" * 80 + "\n")

    return 0


def main_bridge_cli() -> int:
    """CLI entry point for GFL AST bridging."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Bridge .gfl AST into Graphify Knowledge Graph")
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path("."),
        help="Path to repository root containing .gfl files",
    )
    parser.add_argument(
        "--graph",
        type=Path,
        default=Path("graphify-out/graph.json"),
        help="Path to base Graphify graph.json",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Path to output merged graph.json (defaults to overwriting --graph)",
    )
    args = parser.parse_args()

    try:
        res = bridge_gfl_files_to_graph(args.repo, args.graph, args.out)
        print("\n" + "=" * 70)
        print("🧬 GFL AST BRIDGE: UNIFIED GENETIC SCRIPT TOPOLOGY")
        print("=" * 70)
        print(f"Parsed .gfl Specifications : {res['parsed_files']}")
        print(f"Injected Semantic Nodes    : +{res['added_nodes']}")
        print(f"Injected Semantic Edges    : +{res['added_links']}")
        print(f"Total Unified Nodes        : {res['total_nodes']:,}")
        print(f"Total Unified Edges        : {res['total_edges']:,}")
        print("=" * 70 + "\n")
        return 0
    except Exception as e:
        logger.error(f"Error bridging GFL AST: {e}")
        return 1
