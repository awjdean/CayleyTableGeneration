import os
import sys

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from transformation_algebra.comparing_algebras.compare_algebras import compare_algebras
from transformation_algebra.comparing_algebras.enhance_equiv_classes import (
    find_missing_elements,
    merge_missing_elements,
)
from transformation_algebra.comparing_algebras.relabeling import (
    relabel_algebra_components,
)
from transformation_algebra.transformation_algebra import TransformationAlgebra


def main():
    algebra1_name = "gridworld_2x2_wall_2"
    algebra2_name = "gridworld_2x2_wall_3"

    # Load algebras
    print("\nLoading algebras...")
    algebra1 = TransformationAlgebra(name=algebra1_name)
    algebra1.load()

    algebra2 = TransformationAlgebra(name=algebra2_name)
    algebra2.load()

    # Get missing equivalence classes
    missing_elements_classes1, missing_elements_classes2 = find_missing_elements(
        algebra1, algebra2
    )

    print(f"\nMissing equivalence classes for {algebra1_name}:")
    print(missing_elements_classes1)
    print(f"\nMissing equivalence classes for {algebra2_name}:")
    print(missing_elements_classes2)

    # Create enhanced algebras
    print(f"\nMerging missing elements into {algebra1_name}...")
    enhanced_algebra1 = merge_missing_elements(algebra1, missing_elements_classes1)

    print(f"\nMerging missing elements into {algebra2_name}...")
    enhanced_algebra2 = merge_missing_elements(algebra2, missing_elements_classes2)

    # Save the enhanced algebras
    print("\nSaving enhanced algebras...")
    enhanced_algebra1.save(path=None)
    enhanced_algebra2.save(path=None)

    print(
        f"\nEnhanced algebras saved as: {enhanced_algebra1.name} and"
        f" {enhanced_algebra2.name}"
    )

    # Relabel the enhanced algebras
    print("\nRelabeling enhanced algebras...")
    relabeled_algebra1 = relabel_algebra_components(enhanced_algebra1)
    relabeled_algebra2 = relabel_algebra_components(enhanced_algebra2)

    # Save the relabeled algebras
    print("\nSaving relabeled algebras...")
    relabeled_algebra1.save(path=None)
    relabeled_algebra2.save(path=None)
    print(
        f"\nRelabeled algebras saved as: {relabeled_algebra1.name} and"
        f" {relabeled_algebra2.name}"
    )

    # Compare the relabeled algebras in detail
    print("\nComparing relabeled algebras...")
    are_same = compare_algebras(relabeled_algebra1, relabeled_algebra2)
    print(f"\nRelabeled algebras are {'the same' if are_same else 'different'}")


if __name__ == "__main__":
    main()
