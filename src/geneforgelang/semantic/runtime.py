class BeliefState:
    def __init__(self):
        self.statuses = {}


class Epistemic:
    def __init__(self):
        self.belief_state = BeliefState()


class SemanticRuntime:
    def __init__(self):
        self.epistemic = Epistemic()
