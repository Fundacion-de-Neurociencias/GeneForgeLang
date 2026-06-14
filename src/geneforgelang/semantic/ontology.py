class SemanticOntology:
    def __init__(self):
        self.terms = {}

    def has(self, term: str) -> bool:
        return term in self.terms
