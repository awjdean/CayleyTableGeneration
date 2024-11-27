class TransformationAlgebra:
    def __init__(self, name) -> None:
        self._algebra_parameters = None
        self.name = name

        # Cayley tables generation.
        self.cayley_table_states = None
        self.cayley_table_actions = None
        self.equivalence_classes = None

    def generate_cayley_table_states(self):
        pass

    def generate_cayley_table_actions(self):
        pass

    def save_cayley_tables(self):
        pass

    def load_cayley_tables(self):
        pass
