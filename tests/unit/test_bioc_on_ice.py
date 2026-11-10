"""Unit tests for Bioconductor on Ice (bioc-on-ice) Lakehouse & Frozen Annotations.

Grounded in bioc-on-ice (Sean Davis, 2026; https://bioconice.cancerdatasci.org):
- Epistemic Pinning: Binds GFL protocols to frozen biological releases (e.g. 2026-11-08).
- Pushdown Execution: Zero-download DuckDB / Arrow query engine over Cloudflare R2 Parquet files.
- Lakehouse Ground Truth: Ensembl/NCBI gene & transcript resolution and ontology CURIE validation.
"""

from typing import Any

import pytest
from geneforgelang.core.bioc_ice_engine import BiocOnIceEngine
from geneforgelang.core.gftypes import (
    GFLAST,
    BiocIceContract,
    BiocReleaseMetadata,
    BiocSchemaType,
    LakehouseQueryBackend,
    LakehouseQueryContract,
    LakehouseTableMetadata,
    ReferenceGenomeBuild,
)
from geneforgelang.core.parser import parse_gfl
from geneforgelang.core.validator import EnhancedSemanticValidator, ErrorCodes


class TestBiocIceTypes:
    """Test lakehouse enums, metadata classes, and contracts."""

    def test_enums_and_schemas(self) -> None:
        """Verify all 7 lakehouse schemas and execution backends."""
        assert BiocSchemaType.ANNOTATION.value == "annotation"
        assert BiocSchemaType.CLINICAL.value == "clinical"
        assert BiocSchemaType.ONTOLOGY.value == "ontology"
        assert BiocSchemaType.PROVENANCE.value == "provenance"
        assert BiocSchemaType.RAW.value == "raw"
        assert BiocSchemaType.REFERENCE.value == "reference"
        assert BiocSchemaType.RESOURCE.value == "resource"
        assert len(BiocSchemaType) == 7

        assert LakehouseQueryBackend.DUCKDB_HTTPFS.value == "duckdb_httpfs"
        assert LakehouseQueryBackend.ARROW_STREAMING.value == "arrow_streaming"
        assert LakehouseQueryBackend.MANIFEST_INDEX.value == "manifest_index"

        assert ReferenceGenomeBuild.GRCH38.value == "GRCh38"
        assert ReferenceGenomeBuild.T2T_CHM13.value == "T2T-CHM13"

    def test_lakehouse_table_metadata(self) -> None:
        """Verify LakehouseTableMetadata serialization and deserialization."""
        meta = LakehouseTableMetadata(
            schema=BiocSchemaType.ANNOTATION,
            table="gene",
            path="annotation/gene.parquet",
            row_count=70000,
            bytes_size=5000000,
            sha256="abc123def456",
            comment="Ensembl v112 gene annotations",
        )
        d = meta.to_dict()
        assert d["schema"] == "annotation"
        assert d["table"] == "gene"
        assert d["row_count"] == 70000

        restored = LakehouseTableMetadata.from_dict(d)
        assert restored.table == "gene"
        assert restored.schema == BiocSchemaType.ANNOTATION
        assert restored.bytes_size == 5000000

    def test_bioc_release_metadata(self) -> None:
        """Verify BiocReleaseMetadata serialization and table indexing."""
        tbl = LakehouseTableMetadata(
            schema=BiocSchemaType.ONTOLOGY,
            table="term",
            path="ontology/term.parquet",
            row_count=500000,
            bytes_size=12000000,
            sha256="abc123def456",
        )
        release = BiocReleaseMetadata(
            manifest_version=1,
            release_id="2026-11-08",
            published_at="2026-11-08T00:00:00Z",
            git_sha="4771ea8db7f59ca5fd78f64ff0a8ff1f432f3966",
            tables=[tbl],
        )
        d = release.to_dict()
        assert d["release_id"] == "2026-11-08"
        assert len(d["tables"]) == 1
        assert d["tables"][0]["table"] == "term"

        restored = BiocReleaseMetadata.from_dict(d)
        assert restored.release_id == "2026-11-08"
        assert len(restored.tables) == 1
        assert restored.tables[0].table == "term"

    def test_lakehouse_query_contract(self) -> None:
        """Verify LakehouseQueryContract structure."""
        q = LakehouseQueryContract(
            schema=BiocSchemaType.ANNOTATION,
            table="gene",
            columns=["gene_id", "symbol", "chromosome"],
            filter_sql="symbol = 'GZMB'",
            limit=10,
        )
        d = q.to_dict()
        assert d["schema"] == "annotation"
        assert d["table"] == "gene"
        assert d["limit"] == 10

        restored = LakehouseQueryContract.from_dict(d)
        assert restored.schema == BiocSchemaType.ANNOTATION
        assert restored.table == "gene"
        assert restored.columns == ["gene_id", "symbol", "chromosome"]

    def test_bioc_ice_contract_and_aliases(self) -> None:
        """Verify BiocIceContract with backend aliases resolution."""
        data = {
            "release_id": "2026-11-08",
            "genome_build": "GRCh38",
            "query_backend": "duckdb",  # ergonomic alias
            "pinned_tables": ["annotation.gene", "ontology.terms"],
            "queries": [
                {
                    "schema": "annotation",
                    "table": "gene",
                    "filter_sql": "symbol = 'KRAS'",
                }
            ],
        }
        contract = BiocIceContract.from_dict(data)
        assert contract.release_id == "2026-11-08"
        assert contract.genome_build == ReferenceGenomeBuild.GRCH38
        assert contract.query_backend == LakehouseQueryBackend.DUCKDB_HTTPFS
        assert len(contract.queries) == 1
        assert contract.pinned_tables == ["annotation.gene", "ontology.terms"]

        # Test arrow alias
        data["query_backend"] = "arrow"
        contract_arrow = BiocIceContract.from_dict(data)
        assert contract_arrow.query_backend == LakehouseQueryBackend.ARROW_STREAMING

    def test_gflast_aliases(self) -> None:
        """Verify GFLAST support for bioc_reference, lakehouse_reference, and bioc_on_ice."""
        contract = BiocIceContract(release_id="2026-11-08")
        ast1 = GFLAST(bioc_reference=contract)
        assert ast1.bioc_reference is not None
        assert ast1.to_dict()["bioc_reference"]["release_id"] == "2026-11-08"

        # Verify from_dict restores bioc_reference from lakehouse_reference alias
        restored = GFLAST.from_dict({"lakehouse_reference": contract.to_dict()})
        assert restored.bioc_reference is not None
        assert restored.bioc_reference.release_id == "2026-11-08"


class TestBiocOnIceEngine:
    """Test live/cached manifest retrieval, query execution, and biological resolution."""

    @pytest.fixture
    def engine(self) -> BiocOnIceEngine:
        return BiocOnIceEngine()

    def test_manifest_retrieval(self, engine: BiocOnIceEngine) -> None:
        """Verify that manifest is successfully fetched and contains 81 tables."""
        manifest = engine.fetch_manifest()
        assert manifest is not None
        assert manifest.manifest_version >= 1
        assert len(manifest.tables) == 81
        assert manifest.git_sha != ""

    def test_list_tables(self, engine: BiocOnIceEngine) -> None:
        """Verify listing tables with schema filtering."""
        all_metadata = engine.list_tables()
        assert len(all_metadata) == 81
        all_tables = [f"{t.schema.value}.{t.table}" for t in all_metadata]
        assert "annotation.gene" in all_tables
        assert "annotation.transcript" in all_tables
        assert "ontology.term" in all_tables
        assert "clinical.gwas_catalog__study" in all_tables

        annotation_tables = engine.list_tables(schema="annotation")
        assert len(annotation_tables) >= 5
        assert all(t.schema == BiocSchemaType.ANNOTATION for t in annotation_tables)

    def test_get_table_metadata(self, engine: BiocOnIceEngine) -> None:
        """Verify retrieving specific table metadata."""
        meta = engine.get_table_metadata("annotation.gene")
        assert meta is not None
        assert meta.table == "gene"
        assert meta.schema == BiocSchemaType.ANNOTATION
        assert meta.path.endswith(".parquet")
        assert len(meta.sha256) > 0

    def test_resolve_gene(self, engine: BiocOnIceEngine) -> None:
        """Verify ground-truth gene symbol resolution against reference lakehouse."""
        # Test GZMB (chromosome 14)
        gzmb = engine.resolve_gene("GZMB")
        assert gzmb is not None
        assert gzmb["symbol"] == "GZMB"
        assert gzmb["chromosome"] in ("chr14", "14")
        assert gzmb["biotype"] == "protein_coding"

        # Test KRAS (chromosome 12)
        kras = engine.resolve_gene("KRAS")
        assert kras is not None
        assert kras["symbol"] == "KRAS"
        assert kras["chromosome"] in ("chr12", "12")

        # Test TP53 (chromosome 17)
        tp53 = engine.resolve_gene("TP53")
        assert tp53 is not None
        assert tp53["symbol"] == "TP53"
        assert tp53["chromosome"] in ("chr17", "17")

        # Test unknown gene returns None
        unknown = engine.resolve_gene("NON_EXISTENT_GENE_XYZ")
        assert unknown is None

    def test_validate_ontology_curie(self, engine: BiocOnIceEngine) -> None:
        """Verify CURIE validation for Cell Ontology, GO, DOID, HP."""
        # Valid CURIEs
        assert engine.validate_ontology_curie("CL:0000938") is True
        assert engine.validate_ontology_curie("GO:0006955") is True
        assert engine.validate_ontology_curie("DOID:14330") is True
        assert engine.validate_ontology_curie("HP:0001250") is True

        # Invalid CURIEs
        assert engine.validate_ontology_curie("invalid_curie") is False
        assert engine.validate_ontology_curie("") is False
        assert engine.validate_ontology_curie("CL:") is False

    def test_verify_release_integrity(self, engine: BiocOnIceEngine) -> None:
        """Verify cryptographic integrity report across all tables."""
        report = engine.verify_release_integrity()
        assert report["total_tables"] == 81
        assert report["valid_tables"] >= 80
        assert report["corrupted_tables"] == []
        assert report["integrity_ratio"] >= 0.98

    def test_query_execution(self, engine: BiocOnIceEngine) -> None:
        """Verify executing a LakehouseQueryContract via the manifest index backend."""
        query = LakehouseQueryContract(
            schema=BiocSchemaType.ANNOTATION,
            table="gene",
            columns=["gene_id", "symbol", "chromosome"],
            limit=5,
        )
        res = engine.query(query, backend=LakehouseQueryBackend.MANIFEST_INDEX)
        assert res["schema"] == "annotation"
        assert res["table"] == "gene"
        assert res["backend"] == "manifest_index"
        assert "rows" in res
        assert len(res["rows"]) <= 5


class TestBiocIceValidator:
    """Test EnhancedSemanticValidator rules for bioc_reference blocks."""

    @pytest.fixture
    def validator(self) -> EnhancedSemanticValidator:
        return EnhancedSemanticValidator()

    def test_valid_exemplar_gfl(self, validator: EnhancedSemanticValidator) -> None:
        """Verify that the official exemplar .gfl program validates cleanly with 0 errors."""
        with open("examples/bioc_on_ice_lakehouse_reference.gfl", encoding="utf-8") as f:
            content = f.read()

        ast = parse_gfl(content)
        assert ast is not None
        result = validator.validate_ast(ast)
        assert len(result.errors) == 0, f"Validation errors: {[e.message for e in result.errors]}"

    def test_validator_rejects_invalid_release(self, validator: EnhancedSemanticValidator) -> None:
        """Validator must reject invalid release format."""
        ast = {
            "bioc_reference": {
                "release_id": "completely_unrecognized_version_tag",
            }
        }
        result = validator.validate_ast(ast)
        assert any(e.code == ErrorCodes.SEMANTIC_INVALID_PARAMETER for e in result.errors)
        assert any("Invalid release_id" in e.message for e in result.errors)

    def test_validator_rejects_invalid_genome_build(self, validator: EnhancedSemanticValidator) -> None:
        """Validator must reject unsupported genome build."""
        ast = {
            "bioc_reference": {
                "release_id": "latest",
                "genome_build": "HG18_ANCIENT",
            }
        }
        result = validator.validate_ast(ast)
        assert any(e.code == ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE for e in result.errors)
        assert any("Invalid genome_build" in e.message for e in result.errors)

    def test_validator_rejects_invalid_backend(self, validator: EnhancedSemanticValidator) -> None:
        """Validator must reject unsupported execution backend."""
        ast = {
            "bioc_reference": {
                "release_id": "latest",
                "query_backend": "oracle_database_12c",
            }
        }
        result = validator.validate_ast(ast)
        assert any(e.code == ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE for e in result.errors)
        assert any("Invalid query_backend" in e.message for e in result.errors)

    def test_validator_rejects_invalid_schema(self, validator: EnhancedSemanticValidator) -> None:
        """Validator must reject queries with invalid lakehouse schema."""
        ast = {
            "bioc_reference": {
                "release_id": "latest",
                "queries": [
                    {
                        "schema": "non_existent_schema",
                        "table": "gene",
                    }
                ],
            }
        }
        result = validator.validate_ast(ast)
        assert any(e.code == ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE for e in result.errors)
        assert any("Invalid schema 'non_existent_schema'" in e.message for e in result.errors)

    def test_validator_rejects_invalid_limit(self, validator: EnhancedSemanticValidator) -> None:
        """Validator must reject queries with limit < 1."""
        ast = {
            "bioc_reference": {
                "release_id": "latest",
                "queries": [
                    {
                        "schema": "annotation",
                        "table": "gene",
                        "limit": -5,
                    }
                ],
            }
        }
        result = validator.validate_ast(ast)
        assert any(e.code == ErrorCodes.SEMANTIC_INVALID_PARAMETER for e in result.errors)
        assert any("limit (-5)" in e.message for e in result.errors)

    def test_validator_rejects_empty_table(self, validator: EnhancedSemanticValidator) -> None:
        """Validator must reject queries without a table name."""
        ast = {
            "bioc_reference": {
                "release_id": "latest",
                "queries": [
                    {
                        "schema": "annotation",
                        "table": "",
                    }
                ],
            }
        }
        result = validator.validate_ast(ast)
        assert any(e.code == ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD for e in result.errors)
        assert any("must specify a non-empty 'table' name" in e.message for e in result.errors)
