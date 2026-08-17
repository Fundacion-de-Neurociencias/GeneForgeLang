class RFdiffusionPlugin(GeneratorPlugin):
    @property
    def supported_entities(self) -> list[EntityType]:
        return [EntityType.PROTEIN_SEQUENCE]

    def generate(
        self, entity: str, objective: dict, constraints: list[str], count: int, **kwargs
    ) -> list[DesignCandidate]:
        ...