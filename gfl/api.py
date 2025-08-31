"""GeneForgeLang Public API.

This module exposes a small, stable interface intended for consumption by
third-party applications. Internals (lexer, parser variants, demos) may evolve
without breaking this layer.

Example:
    Basic usage of the GFL API:

    >>> from gfl.api import parse, validate, infer
    >>> gfl_text = '''
    ... experiment:
    ...   tool: CRISPR_cas9
    ...   type: gene_editing
    ...   params:
    ...     target_gene: TP53
    ... '''
    >>> ast = parse(gfl_text)
    >>> errors = validate(ast)
    >>> print(f"Valid: {not errors}")
    Valid: True
"""

from __future__ import annotations

from typing import Any, Dict, List, Union, Optional

from gfl import parser as _parser
from gfl.error_handling import EnhancedValidationResult
from gfl.inference_engine import InferenceEngine as _InferenceEngine
from gfl.performance import cached, get_monitor
from gfl.prob_rules import default_rules
from gfl.semantic_validator import validate as _validate

# Optional execution engine import
try:
    from gfl.execution_engine import (
        execute_gfl_ast,
        validate_execution_requirements,
        ExecutionError,
        GFLExecutionEngine,
    )

    HAS_EXECUTION_ENGINE = True
except ImportError:
    HAS_EXECUTION_ENGINE = False
    execute_gfl_ast = None
    validate_execution_requirements = None
    ExecutionError = None
    GFLExecutionEngine = None

# Optional grammar parser import
try:
    from gfl.grammar_parser import parse_gfl_grammar

    HAS_GRAMMAR_PARSER = True
except ImportError:
    HAS_GRAMMAR_PARSER = False
    parse_gfl_grammar = None


def parse(
    text: str, use_grammar: bool = False, filename: str = "<input>"
) -> Dict[str, Any]:
    """Parse GFL source into a Python dict AST.

    Supports both YAML-based parsing (legacy) and grammar-based parsing (advanced).
    Grammar-based parsing provides better error messages and supports more advanced
    syntax features.

    Args:
        text: GFL source code as a string. Must be valid GFL syntax.
        use_grammar: If True, use the grammar-based parser (requires PLY).
                    If False, use the YAML-based parser (legacy).
        filename: Source filename for better error reporting.

    Returns:
        Dictionary representing the AST structure with top-level blocks like
        'experiment', 'analyze', 'simulate', etc.

    Raises:
        yaml.YAMLError: If YAML parsing fails (legacy parser).
        GFLSyntaxError: If grammar parsing fails (grammar parser).
        ValueError: If the input text is empty or malformed.
        ImportError: If grammar parser is requested but PLY is not available.

    Example:
        YAML-based parsing (legacy):
        >>> ast = parse('''
        ... experiment:
        ...   tool: CRISPR_cas9
        ...   type: gene_editing
        ...   params:
        ...     target_gene: TP53
        ... ''')
        >>> print(ast['experiment']['tool'])
        CRISPR_cas9

        Grammar-based parsing (advanced):
        >>> result = parse('''
        ... experiment:
        ...   tool: CRISPR_cas9
        ...   type: gene_editing
        ... ''', use_grammar=True)
        >>> print(result['type'])
        program
    """
    with get_monitor().time_operation("api_parse"):
        if use_grammar:
            if not HAS_GRAMMAR_PARSER:
                raise ImportError(
                    "Grammar parser not available. Install PLY dependency."
                )

            parse_result = parse_gfl_grammar(text, filename)

            if not parse_result.is_valid:
                # Convert enhanced errors to simple exception for API compatibility
                error_messages = []
                for error in parse_result.syntax_errors + parse_result.semantic_errors:
                    if error.location:
                        error_messages.append(f"{error.location}: {error.message}")
                    else:
                        error_messages.append(error.message)

                from gfl.grammar_parser import GFLSyntaxError

                raise GFLSyntaxError("\n".join(error_messages))

            return parse_result.ast
        else:
            return _parser.parse_gfl(text)


@cached(cache_name="schema_validation", ttl=600.0, max_size=500)
def validate(
    ast: Dict[str, Any], enhanced: bool = False
) -> Union[List[str], EnhancedValidationResult]:
    """Return validation errors for the given AST.

    Performs semantic validation on the parsed AST to ensure it follows
    GFL constraints and best practices. Results are cached for performance.

    Args:
        ast: Dictionary AST returned from parse(). Must be a valid AST structure.
        enhanced: If True, return EnhancedValidationResult with rich error context.
                 If False, return legacy list of error strings.

    Returns:
        List of error messages as strings (legacy mode) or EnhancedValidationResult
        with detailed error information, suggested fixes, and context (enhanced mode).

    Example:
        Legacy mode:
        >>> errors = validate(ast)
        >>> if errors:
        ...     print(f"Found {len(errors)} errors")

        Enhanced mode:
        >>> result = validate(ast, enhanced=True)
        >>> if not result.is_valid:
        ...     print(f"Found {len(result.semantic_errors)} errors")
        ...     for error in result.semantic_errors:
        ...         print(f"  {error.location}: {error.message}")
        ...         for fix in error.suggested_fixes:
        ...             print(f"    Suggestion: {fix.description}")
    """
    with get_monitor().time_operation("api_validate"):
        return _validate(ast, enhanced=enhanced)


def infer(
    model,
    ast: Dict[str, Any],
    enhanced: bool = False,
    model_name: Optional[str] = None,
    explain: bool = True,
) -> Dict[str, Any]:
    """Run probabilistic post-processing with a provided model.

    Executes inference on the validated AST using the provided machine learning
    model to generate predictions and confidence scores. Supports both legacy
    and enhanced inference modes.

    Args:
        model: Machine learning model that must expose a predict() method.
               The predict method should accept Dict[str, Any] features and
               return Dict[str, Any] predictions.
        ast: Dictionary AST from parse(). Should be validated before inference.
        enhanced: If True, use enhanced inference engine if available.
        model_name: Specific enhanced model to use ("heuristic", "protein_generation", etc.)
        explain: If True, include detailed explanations in results.

    Returns:
        Dictionary containing inference results with at least:
        - 'label': Predicted outcome/classification
        - 'confidence': Confidence score (0.0-1.0)
        - 'explanation': Human-readable explanation (optional)

        Enhanced mode may include additional fields:
        - 'enhanced_result': Detailed InferenceResult object
        - 'feature_importance': Feature importance scores
        - 'model_metadata': Model-specific metadata

    Raises:
        AttributeError: If model doesn't have a predict() method.
        ValueError: If AST is malformed or incompatible with model.

    Example:
        Legacy inference:
        >>> from gfl.models.dummy import DummyGeneModel
        >>> model = DummyGeneModel()
        >>> ast = parse('experiment:\n  tool: CRISPR_cas9\n  type: gene_editing')
        >>> result = infer(model, ast)
        >>> print(f"Prediction: {result['label']} (confidence: {result['confidence']})")
        Prediction: edited (confidence: 0.85)

        Enhanced inference:
        >>> result = infer(model, ast, enhanced=True, model_name="heuristic")
        >>> print(f"Enhanced: {result['enhanced_result']['explanation']}")
    """
    with get_monitor().time_operation("api_infer"):
        engine = _InferenceEngine(model)

        # Try enhanced inference if requested and available
        if enhanced:
            try:
                # Import here to avoid circular imports
                from gfl.enhanced_inference_engine import get_inference_engine

                enhanced_engine = get_inference_engine()

                # Extract features from AST
                features = engine._extract_features(ast)

                # Use enhanced prediction
                model_name = model_name or "heuristic"
                enhanced_result = enhanced_engine.predict(
                    model_name, features, explain=explain
                )

                # Return enhanced format
                return {
                    "label": str(enhanced_result.prediction),
                    "confidence": enhanced_result.confidence,
                    "explanation": enhanced_result.explanation,
                    "enhanced_result": enhanced_result.to_dict(),
                    "features_used": features,
                    "model_used": model_name,
                }

            except Exception as e:
                # Fall back to legacy inference if enhanced fails
                import logging

                logging.warning(f"Enhanced inference failed, using legacy: {e}")

        # Legacy inference path
        _ = default_rules  # noqa: F401 (documented side-channel)
        return engine.predict_effect(ast, enhanced=False)


def parse_enhanced(
    text: str, use_grammar: bool = True, filename: str = "<input>"
) -> EnhancedValidationResult:
    """Parse GFL source with enhanced error reporting.

    This function provides detailed parsing results with rich error information,
    source locations, and suggested fixes. Recommended for development tools
    and IDEs.

    Args:
        text: GFL source code as a string.
        use_grammar: If True, use grammar-based parser. If False, use YAML parser
                    with basic error wrapping.
        filename: Source filename for error reporting.

    Returns:
        EnhancedValidationResult with detailed parsing information including:
        - AST if parsing succeeded
        - Detailed error information with locations
        - Suggested fixes for common issues

    Example:
        >>> result = parse_enhanced('''
        ... experiment:
        ...   tool: CRISPR_cas9
        ...   invalid_syntax here
        ... ''')
        >>> if not result.is_valid:
        ...     for error in result.syntax_errors:
        ...         print(f"{error.location}: {error.message}")
        ...         for fix in error.suggested_fixes:
        ...             print(f"  Suggestion: {fix.description}")
    """
    with get_monitor().time_operation("api_parse_enhanced"):
        if use_grammar and HAS_GRAMMAR_PARSER:
            return parse_gfl_grammar(text, filename)
        else:
            # Fallback to YAML parser with basic error wrapping
            from gfl.error_handling import (
                EnhancedValidationError,
                ErrorCategory,
                ErrorSeverity,
            )

            try:
                ast = _parser.parse_gfl(text)
                return EnhancedValidationResult(
                    is_valid=True,
                    ast=ast,
                    syntax_errors=[],
                    semantic_errors=[],
                    schema_errors=[],
                )
            except Exception as e:
                error = EnhancedValidationError(
                    message=str(e),
                    code="YAML_PARSE_ERROR",
                    severity=ErrorSeverity.ERROR,
                    category=ErrorCategory.SYNTAX,
                )
                return EnhancedValidationResult(
                    is_valid=False,
                    syntax_errors=[error],
                    semantic_errors=[],
                    schema_errors=[],
                )


# Enhanced inference convenience functions


def infer_enhanced(
    ast: Dict[str, Any], model_name: str = "heuristic", explain: bool = True
) -> Dict[str, Any]:
    """Enhanced inference using advanced ML models.

    Convenience function for enhanced inference without requiring a model instance.

    Args:
        ast: Dictionary AST from parse()
        model_name: Model to use ("heuristic", "genomic_classification",
                   "protein_generation", "multimodal")
        explain: Include detailed explanations

    Returns:
        Dictionary with enhanced inference results

    Example:
        >>> ast = parse('experiment:\n  tool: CRISPR_cas9')
        >>> result = infer_enhanced(ast, "genomic_classification")
        >>> print(result['explanation'])
    """
    try:
        from gfl.enhanced_inference_engine import get_inference_engine
        from gfl.inference_engine import InferenceEngine
        from gfl.models.dummy import DummyGeneModel

        # Create temporary engine to extract features
        temp_engine = InferenceEngine(DummyGeneModel())
        features = temp_engine._extract_features(ast)

        # Use enhanced inference
        enhanced_engine = get_inference_engine()
        result = enhanced_engine.predict(model_name, features, explain=explain)

        return {
            "label": str(result.prediction),
            "confidence": result.confidence,
            "explanation": result.explanation,
            "enhanced_result": result.to_dict(),
            "features_used": features,
            "model_used": model_name,
        }

    except ImportError:
        raise ImportError("Enhanced inference engine not available")


def compare_inference_models(
    ast: Dict[str, Any], model_names: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Compare predictions across multiple inference models.

    Args:
        ast: Dictionary AST from parse()
        model_names: List of model names to compare. If None, uses all available.

    Returns:
        Dictionary with comparison results for each model

    Example:
        >>> ast = parse('experiment:\n  tool: CRISPR_cas9')
        >>> results = compare_inference_models(ast)
        >>> for model, result in results['comparisons'].items():
        ...     print(f"{model}: {result['prediction']} ({result['confidence']:.2%})")
    """
    try:
        from gfl.enhanced_inference_engine import get_inference_engine
        from gfl.inference_engine import InferenceEngine
        from gfl.models.dummy import DummyGeneModel

        # Extract features
        temp_engine = InferenceEngine(DummyGeneModel())
        features = temp_engine._extract_features(ast)

        # Compare models
        enhanced_engine = get_inference_engine()
        results = enhanced_engine.compare_models(features, model_names)

        return {
            "comparisons": {k: v.to_dict() for k, v in results.items()},
            "features_used": features,
            "available_models": enhanced_engine.list_models(),
        }

    except ImportError:
        raise ImportError("Enhanced inference engine not available")


def execute(
    ast: Dict[str, Any], validate_first: bool = True
) -> Dict[str, Any]:
    """Execute a GFL workflow by dispatching to appropriate plugins.

    This function orchestrates the execution of design and optimize blocks
    by finding and invoking the appropriate plugin implementations.

    Args:
        ast: Dictionary AST from parse(). Should contain 'design' and/or 'optimize' blocks.
        validate_first: If True, validate AST and plugin requirements before execution.

    Returns:
        Dictionary containing execution results:
        - 'design': Results from design block execution (if present)
        - 'optimize': Results from optimize block execution (if present)  
        - 'workflow_state': Information about workflow variables and history

    Raises:
        ImportError: If execution engine is not available.
        ExecutionError: If execution fails due to plugin issues or configuration errors.
        ValueError: If AST is invalid or missing required plugins.

    Example:
        Design block execution:
        >>> ast = parse('''
        ... design:
        ...   entity: ProteinSequence
        ...   model: ProteinVAEGenerator
        ...   objective:
        ...     maximize: stability
        ...   count: 10
        ...   output: designed_proteins
        ... ''')
        >>> result = execute(ast)
        >>> print(f"Generated {result['design']['count']} candidates")
        Generated 10 candidates

        Optimize block execution:
        >>> ast = parse('''
        ... optimize:
        ...   search_space:
        ...     temperature: range(25, 42)
        ...     concentration: range(10, 100)
        ...   strategy:
        ...     name: BayesianOptimization
        ...   objective:
        ...     maximize: efficiency
        ...   budget:
        ...     max_experiments: 20
        ...   run:
        ...     experiment:
        ...       tool: CRISPR_cas9
        ...       params:
        ...         temp: ${temperature}
        ...         conc: ${concentration}
        ... ''')
        >>> result = execute(ast)
        >>> best = result['optimize']['best_parameters']
        >>> print(f"Best parameters: {best}")
        Best parameters: {'temperature': 37.2, 'concentration': 75.5}
    """
    if not HAS_EXECUTION_ENGINE:
        raise ImportError(
            "Execution engine not available. Plugin system may not be properly installed."
        )

    with get_monitor().time_operation("api_execute"):
        if validate_first:
            # Validate AST first
            validation_errors = validate(ast)
            if validation_errors:
                error_msg = "; ".join(validation_errors[:3])  # Show first 3 errors
                raise ValueError(f"AST validation failed: {error_msg}")

            # Validate plugin requirements
            plugin_errors = validate_execution_requirements(ast)
            if plugin_errors:
                error_msg = "; ".join(plugin_errors)
                raise ValueError(f"Plugin requirements not met: {error_msg}")

        return execute_gfl_ast(ast)


def validate_plugins(ast: Dict[str, Any]) -> List[str]:
    """Validate that required plugins are available for AST execution.

    Args:
        ast: Dictionary AST from parse()

    Returns:
        List of validation error messages (empty if all plugins available)

    Example:
        >>> ast = parse('''
        ... design:
        ...   entity: ProteinSequence  
        ...   model: NonExistentModel
        ...   count: 10
        ...   output: results
        ... ''')
        >>> errors = validate_plugins(ast)
        >>> if errors:
        ...     print(f"Missing plugins: {errors[0]}")
        Missing plugins: Design model 'NonExistentModel' not available
    """
    if not HAS_EXECUTION_ENGINE:
        return ["Execution engine not available"]

    return validate_execution_requirements(ast)


def list_available_plugins() -> Dict[str, List[str]]:
    """List all available plugins for design and optimize blocks.

    Returns:
        Dictionary with 'generators' and 'optimizers' keys containing
        lists of available plugin names.

    Example:
        >>> plugins = list_available_plugins()
        >>> print(f"Available generators: {plugins['generators']}")
        >>> print(f"Available optimizers: {plugins['optimizers']}")
        Available generators: ['ProteinVAEGenerator', 'MoleculeTransformerGenerator']
        Available optimizers: ['BayesianOptimizer']
    """
    if not HAS_EXECUTION_ENGINE:
        return {"generators": [], "optimizers": []}

    try:
        from gfl.plugins import get_available_generators, get_available_optimizers

        generators = get_available_generators()
        optimizers = get_available_optimizers()

        return {
            "generators": list(generators.keys()),
            "optimizers": list(optimizers.keys()),
        }
    except ImportError:
        return {"generators": [], "optimizers": []}


def get_api_info() -> Dict[str, Any]:
    """Get information about the GFL API and available features.

    Returns:
        Dictionary containing API version, available features, and system info.
    """
    info = {
        "api_version": "0.1.0",
        "gfl_version": "0.1.0",
        "features": {
            "basic_parsing": True,
            "grammar_parsing": HAS_GRAMMAR_PARSER,
            "enhanced_inference": True,
            "model_comparison": True,
            "workflow_execution": HAS_EXECUTION_ENGINE,
            "plugin_system": HAS_EXECUTION_ENGINE,
        },
        "available_parsers": ["yaml"],
        "inference_models": ["heuristic"],
        "execution_blocks": [],
    }

    if HAS_GRAMMAR_PARSER:
        info["available_parsers"].append("grammar")

    if HAS_EXECUTION_ENGINE:
        info["execution_blocks"] = ["design", "optimize"]
        
        # Add plugin information
        try:
            plugins = list_available_plugins()
            info["available_plugins"] = plugins
        except Exception:
            info["available_plugins"] = {"generators": [], "optimizers": []}

    try:
        from gfl.enhanced_inference_engine import get_inference_engine

        engine = get_inference_engine()
        info["inference_models"] = engine.list_models()
    except ImportError:
        pass

    return info
    """Get information about the GFL API and available features.

    Returns:
        Dictionary containing API version, available features, and system info.
    """
    info = {
        "api_version": "0.1.0",
        "gfl_version": "0.1.0",
        "features": {
            "basic_parsing": True,
            "grammar_parsing": HAS_GRAMMAR_PARSER,
            "enhanced_inference": True,
            "model_comparison": True,
        },
        "available_parsers": ["yaml"],
        "inference_models": ["heuristic"],
    }

    if HAS_GRAMMAR_PARSER:
        info["available_parsers"].append("grammar")

    try:
        from gfl.enhanced_inference_engine import get_inference_engine

        engine = get_inference_engine()
        info["inference_models"] = engine.list_models()
    except ImportError:
        pass

    return info


__all__ = [
    "parse",
    "validate",
    "infer",
    "execute",
    "validate_plugins", 
    "list_available_plugins",
    "parse_enhanced",
    "infer_enhanced",
    "compare_inference_models",
    "get_api_info",
]
