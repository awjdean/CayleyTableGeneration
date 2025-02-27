"""
This is the group S3, which is also the dihedral group of the trinagle.
"""

import copy
import os
import sys

# Add the project root directory to the Python path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from transformation_algebra.transformation_algebra import TransformationAlgebra
from transformation_algebra.utils.algebra_generation_methods import (
    AlgebraGenerationMethod,
)
from worlds.graphworlds.graphworld8 import GraphWorld8

# Create GraphWorld8 instance
world = GraphWorld8()
world.generate_min_action_transformation_matrix()
world.draw_graph()

# Create and generate global transformation algebra
global_algebra = TransformationAlgebra("graphworld8_global")
global_algebra.generate(world, method=AlgebraGenerationMethod.ACTION_FUNCTION)
global_algebra.check_properties()
global_algebra.print_properties()
# global_algebra.save(None)

print("\n" + "=" * 80 + "\n")

# Create and generate local transformation algebra.
initial_state = (1,)
local_algebra = TransformationAlgebra("graphworld8_local")
local_algebra.generate(
    world,
    initial_state=initial_state,
    method=AlgebraGenerationMethod.LOCAL_ACTION_FUNCTION,
)
local_algebra.check_properties()
local_algebra.print_properties(True)
local_algebra.save(None)
print(local_algebra.cayley_table_actions.data)


def check_all_local_algebras_equal():
    local_cayley_tables = {}

    states = [(1,), (2,), (3,), (4,), (5,), (6,)]
    for initial_state in states:
        local_algebra = TransformationAlgebra("graphworld8_local")
        local_algebra.generate(
            world,
            initial_state=initial_state,
            method=AlgebraGenerationMethod.LOCAL_ACTION_FUNCTION,
        )
        local_algebra.check_properties()
        # local_algebra.print_properties(False)

        # Get Cayley table actions data and store
        local_cayley_tables[initial_state] = copy.deepcopy(
            local_algebra.cayley_table_actions.data
        )

    return local_cayley_tables


local_cayley_tables = check_all_local_algebras_equal()


def check_if_identical(cayley_tables):
    for i, (state1, cayley_table1) in enumerate(cayley_tables.items()):
        for j, (state2, cayley_table2) in enumerate(cayley_tables.items()):
            if i == j:
                continue
            if cayley_table1 != cayley_table2:
                print(f"State {state1} and state {state2} are not identical.")
                return False
    return True


print(f"Cayley table check: {check_if_identical(local_cayley_tables)}")
print("DONE")
