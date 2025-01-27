import os
import sys

from worlds.gridworlds2d.gridworld2d_consumable import Gridworld2DConsumable

# Add the project root directory to the Python path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from transformation_algebra.transformation_algebra import TransformationAlgebra
from transformation_algebra.utils.algebra_generation_methods import (
    AlgebraGenerationMethod,
)

# Create a simple gridworld with walls
world = Gridworld2DConsumable(
    grid_shape=(4, 1), consumable_positions=[(1, 0)], consume_strategy="masked"
)
world.generate_min_action_transformation_matrix()

# Create and initialize the transformation algebra
algebra = TransformationAlgebra(name="4x1_gridworld_with_consumable_identity")

# Generate the algebra using the action function method
algebra.generate(world=world, method=AlgebraGenerationMethod.ACTION_FUNCTION)

# Check and print the algebraic properties
algebra.check_properties()
algebra.print_properties(details=False)
print(algebra.equiv_classes)

# Optionally save the algebra
algebra.save(None)  # This will save to ./saved/algebra/2x2_gridworld_with_wall.pkl

# Save the Cayley table as LaTeX
latex_path = os.path.join("saved", "algebra", f"{algebra.name}_cayley.tex")
os.makedirs(os.path.dirname(latex_path), exist_ok=True)

latex_content = algebra.cayley_table_actions.to_latex()
with open(latex_path, "w", encoding="utf-8") as f:
    f.write(latex_content)

print(f"\nLaTeX table saved to: {latex_path}")
