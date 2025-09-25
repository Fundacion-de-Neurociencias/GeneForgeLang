#!/usr/bin/env python3
"""
QA Integration Test Suite for GeneForge Platform
Executes comprehensive testing across all critical areas.
"""

import json
import os
import subprocess
import sys
import time
from typing import Dict, List, Tuple

import requests

# Add gfl to path
sys.path.append(os.path.join(os.path.dirname(__file__), "gfl"))

from gfl.parser import parse_gfl
from gfl.semantic_validator import EnhancedSemanticValidator
from gfl.capability_system import get_engine_capabilities


class QAIntegrationTester:
    """Comprehensive QA testing for GeneForge platform."""
    
    def __init__(self):
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "bugs_found": [],
            "test_details": {}
        }
        self.base_url = "http://localhost:8000"
        
    def run_test(self, test_name: str, test_func) -> bool:
        """Run a single test and record results."""
        self.results["total_tests"] += 1
        print(f"\n🧪 Running: {test_name}")
        
        try:
            success = test_func()
            if success:
                self.results["passed"] += 1
                print(f"✅ PASSED: {test_name}")
            else:
                self.results["failed"] += 1
                print(f"❌ FAILED: {test_name}")
            return success
        except Exception as e:
            self.results["failed"] += 1
            print(f"❌ ERROR in {test_name}: {e}")
            self.results["bugs_found"].append({
                "test": test_name,
                "error": str(e),
                "type": "exception"
            })
            return False
    
    def test_gfl_service_health(self) -> bool:
        """Test 1: GFL Service Health Check"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("status") == "ok"
            return False
        except Exception:
            return False
    
    def test_gfl_parser_basic(self) -> bool:
        """Test 2: Basic GFL Parser Functionality"""
        try:
            test_gfl = """
experiment:
  name: "test_experiment"
  description: "Basic parser test"
"""
            ast = parse_gfl(test_gfl)
            return isinstance(ast, dict) and "experiment" in ast
        except Exception:
            return False
    
    def test_gfl_parser_multi_omic(self) -> bool:
        """Test 3: Multi-Omic Parser Functionality"""
        try:
            test_gfl = """
transcripts:
  - id: "test_transcript"
    gene_source: "TEST"
    exons: [1, 2, 3]

proteins:
  - id: "test_protein"
    translates_from: "transcript(test_transcript)"
    domains:
      - id: "test_domain"
        start: 1
        end: 100
"""
            ast = parse_gfl(test_gfl)
            return ("transcripts" in ast and "proteins" in ast and 
                    len(ast["transcripts"]) > 0 and len(ast["proteins"]) > 0)
        except Exception:
            return False
    
    def test_semantic_validator(self) -> bool:
        """Test 4: Semantic Validator Functionality"""
        try:
            test_gfl = """
transcripts:
  - id: "test_transcript"
    gene_source: "TEST"
    exons: [1, 2, 3]
"""
            ast = parse_gfl(test_gfl)
            capabilities = get_engine_capabilities("advanced")
            validator = EnhancedSemanticValidator(engine_capabilities=capabilities)
            result = validator.validate_ast(ast)
            return len(result.errors) == 0
        except Exception:
            return False
    
    def test_spatial_genomic_features(self) -> bool:
        """Test 5: Spatial Genomic Features"""
        try:
            test_gfl = """
loci:
  - id: "test_locus"
    chromosome: "chr1"
    start: 1000
    end: 2000
    elements:
      - id: "test_element"
        type: "gene"

rules:
  - id: "test_rule"
    if:
      - type: "is_within"
        element: "test_element"
        locus: "test_locus"
    then:
      - type: "set_activity"
        element: "test_element"
        level: "high"
"""
            ast = parse_gfl(test_gfl)
            capabilities = get_engine_capabilities("advanced")
            validator = EnhancedSemanticValidator(engine_capabilities=capabilities)
            result = validator.validate_ast(ast)
            return len(result.errors) == 0
        except Exception:
            return False
    
    def test_conformance_suite_v1_3_0(self) -> bool:
        """Test 6: Conformance Suite v1.3.0"""
        try:
            # Run the conformance suite test
            result = subprocess.run([
                sys.executable, "test_conformance_suite_v1_3_0.py"
            ], capture_output=True, text=True, timeout=60)
            
            # Check if tests passed (look for success indicators in output)
            return "PASSED" in result.stdout and result.returncode == 0
        except Exception:
            return False
    
    def test_multi_omic_v2_0(self) -> bool:
        """Test 7: Multi-Omic v2.0 Capabilities"""
        try:
            # Run the multi-omic test suite
            result = subprocess.run([
                sys.executable, "test_multi_omic_v2_0.py"
            ], capture_output=True, text=True, timeout=60)
            
            # Check if tests passed
            return "PASSED" in result.stdout and result.returncode == 0
        except Exception:
            return False
    
    def test_api_endpoints(self) -> bool:
        """Test 8: API Endpoints Functionality"""
        try:
            # Test parse endpoint
            test_data = {
                "gfl_content": """
experiment:
  name: "api_test"
  description: "API endpoint test"
"""
            }
            
            response = requests.post(
                f"{self.base_url}/parse",
                json=test_data,
                timeout=10
            )
            
            if response.status_code != 200:
                return False
            
            # Test validate endpoint
            response = requests.post(
                f"{self.base_url}/validate",
                json=test_data,
                timeout=10
            )
            
            return response.status_code == 200
        except Exception:
            return False
    
    def test_external_identifiers(self) -> bool:
        """Test 9: External Identifiers Validation"""
        try:
            test_gfl = """
proteins:
  - id: "p53_protein"
    translates_from: "transcript(TP53_transcript)"
    domains:
      - id: "DNA_BindingDomain"
        start: 102
        end: 292
    identifiers:
      uniprot: "P04637"
      refseq: "NP_000537.3"
      pdb: "1TUP"
"""
            ast = parse_gfl(test_gfl)
            capabilities = get_engine_capabilities("advanced")
            validator = EnhancedSemanticValidator(engine_capabilities=capabilities)
            result = validator.validate_ast(ast)
            
            # Should pass validation
            return len(result.errors) == 0
        except Exception:
            return False
    
    def test_capability_system(self) -> bool:
        """Test 10: Capability System"""
        try:
            # Test with basic engine (should have warnings)
            test_gfl = """
transcripts:
  - id: "test_transcript"
    gene_source: "TEST"
    exons: [1, 2, 3]
"""
            ast = parse_gfl(test_gfl)
            capabilities = get_engine_capabilities("basic")
            validator = EnhancedSemanticValidator(engine_capabilities=capabilities)
            result = validator.validate_ast(ast)
            
            # Should have capability warnings for basic engine
            return len(result.warnings) > 0
        except Exception:
            return False
    
    def test_error_handling(self) -> bool:
        """Test 11: Error Handling"""
        try:
            # Test with invalid GFL syntax
            invalid_gfl = """
experiment:
  name: "test"
  invalid_field: [unclosed list
"""
            try:
                ast = parse_gfl(invalid_gfl)
                # Should not reach here - should raise exception
                return False
            except Exception:
                # Expected to raise exception for invalid syntax
                return True
        except Exception:
            return False
    
    def test_performance_basic(self) -> bool:
        """Test 12: Basic Performance"""
        try:
            # Test parsing time for medium-sized GFL
            test_gfl = """
experiment:
  name: "performance_test"
  description: "Testing parsing performance"
  
transcripts:
  - id: "transcript_1"
    gene_source: "GENE1"
    exons: [1, 2, 3, 4, 5]
  - id: "transcript_2"
    gene_source: "GENE2"
    exons: [1, 2, 3]
  - id: "transcript_3"
    gene_source: "GENE3"
    exons: [1, 2, 3, 4, 5, 6, 7]
"""
            start_time = time.time()
            ast = parse_gfl(test_gfl)
            end_time = time.time()
            
            # Should parse in reasonable time (< 1 second)
            parse_time = end_time - start_time
            return parse_time < 1.0
        except Exception:
            return False
    
    def run_all_tests(self) -> Dict:
        """Run all QA tests and return results."""
        print("🚀 Starting GeneForge QA Integration Tests")
        print("=" * 60)
        
        # Core functionality tests
        self.run_test("GFL Service Health", self.test_gfl_service_health)
        self.run_test("Basic GFL Parser", self.test_gfl_parser_basic)
        self.run_test("Multi-Omic Parser", self.test_gfl_parser_multi_omic)
        self.run_test("Semantic Validator", self.test_semantic_validator)
        self.run_test("Spatial Genomic Features", self.test_spatial_genomic_features)
        
        # Comprehensive test suites
        self.run_test("Conformance Suite v1.3.0", self.test_conformance_suite_v1_3_0)
        self.run_test("Multi-Omic v2.0 Capabilities", self.test_multi_omic_v2_0)
        
        # API and integration tests
        self.run_test("API Endpoints", self.test_api_endpoints)
        self.run_test("External Identifiers", self.test_external_identifiers)
        self.run_test("Capability System", self.test_capability_system)
        
        # Quality and performance tests
        self.run_test("Error Handling", self.test_error_handling)
        self.run_test("Basic Performance", self.test_performance_basic)
        
        return self.results
    
    def generate_report(self) -> str:
        """Generate QA test report."""
        total = self.results["total_tests"]
        passed = self.results["passed"]
        failed = self.results["failed"]
        success_rate = (passed / total * 100) if total > 0 else 0
        
        report = f"""
# GeneForge QA Integration Test Report

## Summary
- **Total Tests:** {total}
- **Passed:** {passed}
- **Failed:** {failed}
- **Success Rate:** {success_rate:.1f}%

## Test Results
"""
        
        if self.results["bugs_found"]:
            report += "\n## Bugs Found\n"
            for bug in self.results["bugs_found"]:
                report += f"- **{bug['test']}**: {bug['error']}\n"
        
        if success_rate >= 90:
            report += "\n## Status: ✅ READY FOR BETA\n"
        elif success_rate >= 80:
            report += "\n## Status: ⚠️ NEEDS MINOR FIXES\n"
        else:
            report += "\n## Status: ❌ NEEDS MAJOR FIXES\n"
        
        return report


def main():
    """Main function to run QA tests."""
    tester = QAIntegrationTester()
    results = tester.run_all_tests()
    
    print("\n" + "=" * 60)
    print("📊 QA TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {results['total_tests']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    
    if results['bugs_found']:
        print(f"\n🐛 Bugs Found: {len(results['bugs_found'])}")
        for bug in results['bugs_found']:
            print(f"  - {bug['test']}: {bug['error']}")
    
    success_rate = (results['passed'] / results['total_tests'] * 100) if results['total_tests'] > 0 else 0
    print(f"\nSuccess Rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("🎉 Status: READY FOR BETA!")
    elif success_rate >= 80:
        print("⚠️ Status: Needs minor fixes")
    else:
        print("❌ Status: Needs major fixes")
    
    # Generate detailed report
    report = tester.generate_report()
    with open("QA_TEST_REPORT.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"\n📄 Detailed report saved to: QA_TEST_REPORT.md")
    
    return success_rate >= 90


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
