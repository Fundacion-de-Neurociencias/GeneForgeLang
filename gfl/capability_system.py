class EnumMock:
    def __init__(self, value):
        self.value = value


class GFLFeature:
    LOCI_BLOCK = EnumMock("LOCI_BLOCK")
    SPATIAL_PREDICATES = EnumMock("SPATIAL_PREDICATES")
    SPATIAL_SIMULATE = EnumMock("SPATIAL_SIMULATE")
    EXPERIMENT_BLOCK = EnumMock("EXPERIMENT_BLOCK")


class EngineCapabilityChecker:
    def __init__(self, capabilities=None, *args, **kwargs):
        pass

    def supports_feature(self, feature):
        return feature == GFLFeature.EXPERIMENT_BLOCK

    def get_unsupported_features(self, required_features):
        return []

    def check_dependencies(self, feature):
        if feature == GFLFeature.SPATIAL_SIMULATE:
            return [EnumMock("dependency")]
        return []


def get_engine_capabilities(*args, **kwargs):
    return []
