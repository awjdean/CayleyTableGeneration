import copy
import os
import sys

# Add the project root directory to the Python path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)


from CayleyStatesAlgo.generation.cayley_table_states import CayleyTableStates
from transformation_algebra.comparing_algebras.compare_generation_parameters import (
    compare_generation_parameters,
)
from transformation_algebra.transformation_algebra import TransformationAlgebra
from utils.equiv_classes import EquivClasses


def find_missing_elements(
    algebra1: TransformationAlgebra, algebra2: TransformationAlgebra
) -> tuple[EquivClasses, EquivClasses]:
    """
    Find elements missing from each algebra and create equivalence classes for them.

    Args:
        algebra1: First TransformationAlgebra instance
        algebra2: Second TransformationAlgebra instance

    Returns:
        tuple[EquivClasses, EquivClasses]: Equivalence classes for elements missing from
          each algebra

    Raises:
        ValueError: If the algebras have different generation parameters
    """
    # First check if the algebras have the same generation parameters
    params_match, details = compare_generation_parameters(algebra1, algebra2)
    if not params_match:
        raise ValueError(
            "Cannot find missing elements: algebras have different generation"
            f" parameters.\n\n{details}"
        )

    # Compare elements between algebras
    only_in_1, only_in_2 = compare_algebra_equiv_classes_elements(algebra1, algebra2)

    # Create new EquivClasses for elements missing from algebra1.
    print(f"\nFinding elements from {algebra2.name} missing in {algebra1.name}...")
    missing_elements_classes1 = sort_missing_elements_into_equiv_classes(
        missing_elements=list(only_in_2), target_algebra=algebra1
    )

    # Create new EquivClasses for elements missing from algebra2.
    print(f"\nFinding elements from {algebra1.name} missing in {algebra2.name}...")
    missing_elements_classes2 = sort_missing_elements_into_equiv_classes(
        missing_elements=list(only_in_1), target_algebra=algebra2
    )

    return missing_elements_classes1, missing_elements_classes2


def sort_missing_elements_into_equiv_classes(
    missing_elements: list[str], target_algebra: TransformationAlgebra
) -> EquivClasses:
    """
    Sort missing elements into equivalence classes based on their behavior.

    Args:
        missing_elements: List of elements to classify
        target_algebra: The algebra whose classes we're matching against

    Returns:
        New EquivClasses instance containing the classified elements

    Raises:
        ValueError: If an element has no equivalence class or multiple possible classes
    """
    missing_equiv_classes = EquivClasses()

    cayley_table_states: CayleyTableStates = target_algebra.cayley_table_states
    world = target_algebra._algebra_generation_parameters["world"]
    initial_state = target_algebra._algebra_generation_parameters["initial_state"]

    for element in missing_elements:
        # Find elements in target algebra that behave the same as this element
        equiv_elements = cayley_table_states.find_equiv_elements(
            element, initial_state=initial_state, world=world
        )

        # We expect exactly one equivalent element (the class label)
        if not equiv_elements:
            raise ValueError(
                f"Element '{element}' has no equivalent elements in target algebra"
            )
        if len(equiv_elements) > 1:
            raise ValueError(
                f"Element '{element}' has multiple equivalent elements in target"
                f" algebra: {sorted(equiv_elements.keys())}"
            )

        # Get the class label (the only equivalent element)
        equiv_element_label = next(iter(equiv_elements.keys()))

        # Create the class if it doesn't exist yet
        if equiv_element_label not in missing_equiv_classes.get_labels():
            missing_equiv_classes.create_new_class(
                class_label=equiv_element_label,
                outcome=target_algebra.equiv_classes.get_class_outcome(
                    equiv_element_label
                ),
                elements=[equiv_element_label],
            )

        # Add the element to its class
        missing_equiv_classes.add_element(
            element=element, class_label=equiv_element_label
        )

    return missing_equiv_classes


def compare_algebra_equiv_classes_elements(
    algebra1: TransformationAlgebra, algebra2: TransformationAlgebra
) -> tuple[set[str], set[str]]:
    """
    Compare elements between two algebras and find differences.

    Args:
        algebra1: First TransformationAlgebra instance
        algebra2: Second TransformationAlgebra instance

    Returns:
        tuple[set[str], set[str]]: Elements only in first algebra, elements only in
          second algebra
    """
    elements1 = set(algebra1.equiv_classes.get_all_elements())
    elements2 = set(algebra2.equiv_classes.get_all_elements())

    only_in_1 = elements1 - elements2
    only_in_2 = elements2 - elements1

    if only_in_1 or only_in_2:
        print("\nDifferences in elements:")
        if only_in_1:
            print(f"Elements only in {algebra1.name}: {sorted(only_in_1)}")
        if only_in_2:
            print(f"Elements only in {algebra2.name}: {sorted(only_in_2)}")
    else:
        print("\nNo differences in elements")

    return only_in_1, only_in_2


def merge_missing_elements(
    base_algebra: TransformationAlgebra,
    missing_classes: EquivClasses,
) -> TransformationAlgebra:
    """
    Create a new TransformationAlgebra with missing elements merged in.

    The enhanced algebra will be named {base_algebra.name}_enhanced.
    For example: "gridworld_2x2_wall" -> "gridworld_2x2_wall_enhanced"

    Args:
        base_algebra: The original algebra to enhance
        missing_classes: The equivalence classes containing missing elements

    Returns:
        A new TransformationAlgebra with missing elements added

    Raises:
        ValueError: If missing_classes contains labels not present in base_algebra
    """
    # Check that all class labels in missing_classes exist in base_algebra
    base_labels = set(base_algebra.equiv_classes.get_labels())
    missing_labels = set(missing_classes.get_labels())
    unknown_labels = missing_labels - base_labels

    if unknown_labels:
        raise ValueError(
            "Found equivalence class labels in missing_classes that don't exist in"
            f" base_algebra: {sorted(unknown_labels)}"
        )

    # Create new algebra instance with same name but '_enhanced' suffix
    enhanced_algebra = TransformationAlgebra(name=f"{base_algebra.name}_enhanced")

    # Deep copy generation parameters, but handle world object separately
    params = base_algebra._algebra_generation_parameters
    enhanced_params = {}
    for key, value in params.items():
        if key == "world":
            # World object might not be deep-copyable, use direct reference
            enhanced_params[key] = value
        else:
            # Deep copy other parameters
            enhanced_params[key] = copy.deepcopy(value)

    enhanced_algebra._algebra_generation_parameters = enhanced_params

    # Create new EquivClasses instance and copy base algebra's classes
    merged_equiv = EquivClasses()
    merged_equiv.data = copy.deepcopy(base_algebra.equiv_classes.data)

    # Add each element from missing_classes to the appropriate class
    for class_label in missing_classes.get_labels():
        elements: set[str] = missing_classes.get_class_elements(class_label)
        elements_to_add: set[str] = elements - {class_label}
        for element in elements_to_add:
            merged_equiv.add_element(element, class_label)

    # Set the merged classes in the enhanced algebra
    enhanced_algebra.equiv_classes = merged_equiv

    # Deep copy Cayley tables from base algebra
    enhanced_algebra.cayley_table_states = copy.deepcopy(
        base_algebra.cayley_table_states
    )
    enhanced_algebra.cayley_table_actions = copy.deepcopy(
        base_algebra.cayley_table_actions
    )

    return enhanced_algebra


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

    print(f"\nFinal equivalence classes for {enhanced_algebra1.name}:")
    print(enhanced_algebra1.equiv_classes)
    print(f"\nFinal equivalence classes for {enhanced_algebra2.name}:")
    print(enhanced_algebra2.equiv_classes)

    # Compare the two enhanced algebras
    print("\nComparing the two enhanced algebras:")
    compare_algebra_equiv_classes_elements(enhanced_algebra1, enhanced_algebra2)


if __name__ == "__main__":
    main()
