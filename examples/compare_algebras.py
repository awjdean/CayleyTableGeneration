import os
import sys

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from transformation_algebra.transformation_algebra import TransformationAlgebra


def compare_cayley_tables(table1, table2) -> bool:
    """Compare two Cayley tables for equality."""
    if table1 is None or table2 is None:
        return False

    # Check if tables have same number of elements
    if hasattr(table1, "get_all_actions"):  # For CayleyTableActions
        elements1 = table1.get_all_actions()
        elements2 = table2.get_all_actions()
        if len(elements1) != len(elements2):
            return False
    elif hasattr(table1, "get_row_labels"):  # For CayleyTableStates
        elements1 = table1.get_row_labels()
        elements2 = table2.get_row_labels()
        if len(elements1) != len(elements2):
            return False

    return table1 == table2


def compare_equiv_classes(equiv_classes1, equiv_classes2) -> tuple[bool, str]:
    """
    Compare two equivalence class structures in detail.

    Args:
        equiv_classes1: First EquivClasses object
        equiv_classes2: Second EquivClasses object

    Returns:
        tuple[bool, str]: (whether they match, detailed comparison message)
    """
    if equiv_classes1 == equiv_classes2:
        return True, "Equivalence classes are identical"

    # Get all elements from both classes
    all_elements1 = equiv_classes1.get_all_elements()
    all_elements2 = equiv_classes2.get_all_elements()

    # Check if they contain the same elements
    if set(all_elements1) != set(all_elements2):
        diff1 = set(all_elements1) - set(all_elements2)
        diff2 = set(all_elements2) - set(all_elements1)
        msg = "Elements differ between equivalence classes:\n"
        if diff1:
            msg += f"- Elements only in first algebra: {sorted(diff1)}\n"
        if diff2:
            msg += f"- Elements only in second algebra: {sorted(diff2)}\n"
        return False, msg

    # Compare which elements are grouped together
    differences = []
    for element in all_elements1:
        class1 = equiv_classes1.find_element_class(element)
        class2 = equiv_classes2.find_element_class(element)

        if class1 is None or class2 is None:
            differences.append(f"Element '{element}' not found in one of the classes")
            continue

        elements1 = equiv_classes1.get_class_elements(class1)
        elements2 = equiv_classes2.get_class_elements(class2)

        if elements1 != elements2:
            differences.append(
                f"Element '{element}' belongs to different groups:\n"
                f"- In first algebra: {sorted(elements1)} (labeled as '{class1}')\n"
                f"- In second algebra: {sorted(elements2)} (labeled as '{class2}')"
            )

    if differences:
        msg = "Found differences in equivalence class groupings:\n" + "\n".join(
            differences
        )
        return False, msg

    return True, "Equivalence classes have same groupings but different labels"


def compare_algebras(algebra1_name: str, algebra2_name: str) -> bool:
    """
    Load and compare two algebras to check if they are the same.

    Args:
        algebra1_name: Name of the first algebra
        algebra2_name: Name of the second algebra

    Returns:
        bool: True if the algebras are the same, False otherwise
    """
    # Create and load the first algebra
    algebra1 = TransformationAlgebra(name=algebra1_name)
    algebra1.load()

    # Create and load the second algebra
    algebra2 = TransformationAlgebra(name=algebra2_name)
    algebra2.load()

    print(f"\nComparing algebras: {algebra1_name} vs {algebra2_name}")

    # Compare Cayley table states
    states_match = compare_cayley_tables(
        algebra1.cayley_table_states, algebra2.cayley_table_states
    )
    print(f"Cayley table states match: {states_match}")

    # Compare Cayley table actions
    actions_match = compare_cayley_tables(
        algebra1.cayley_table_actions, algebra2.cayley_table_actions
    )
    if actions_match:
        print(
            f"Cayley table actions match: {actions_match}"
            f" (both have {len(algebra1.cayley_table_actions.get_all_actions())}"
            " elements)"
        )
    else:
        print(f"Cayley table actions match: {actions_match}")
        print(
            "Number of elements:"
            f" {len(algebra1.cayley_table_actions.get_all_actions())}"
            f" vs {len(algebra2.cayley_table_actions.get_all_actions())}"
        )

    # Compare equivalence classes
    equiv_match, equiv_details = compare_equiv_classes(
        algebra1.equiv_classes, algebra2.equiv_classes
    )
    print(f"Equivalence classes match: {equiv_match}")
    if not equiv_match:
        print("\nEquivalence class differences:")
        print(equiv_details)

    # All components must match for algebras to be considered the same
    return states_match and actions_match and equiv_match


def main():
    # Example usage
    algebra1_name = "gridworld_2x2_wall_2"
    algebra2_name = "gridworld_2x2_wall_3"

    are_same = compare_algebras(algebra1_name, algebra2_name)
    print(f"\nAlgebras are {'the same' if are_same else 'different'}")


if __name__ == "__main__":
    main()
