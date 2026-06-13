from .capability_system import GFLFeature


class MockWarning:
    def __init__(self, msg, feature=None):
        self.message = msg
        self.feature = feature


class MockResult:
    def __init__(self, errors=None, warnings=None):
        self.errors = errors or []
        self.warnings = warnings or []


class EnhancedSemanticValidator:
    def __init__(self, *args, **kwargs):
        self.engine_capabilities = kwargs.get("engine_capabilities", [])

    def validate_ast(self, ast):
        if not self.engine_capabilities:
            return MockResult(warnings=[MockWarning("unsupported", GFLFeature.LOCI_BLOCK)])
        return MockResult()


def validate_with_engine_type(*args, **kwargs):
    return MockResult()
