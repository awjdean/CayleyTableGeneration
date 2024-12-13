from cayley_tables.tables.cayley_table_actions import CayleyTableActions
from cayley_tables.tables.cayley_table_states import CayleyTableStates
from cayley_tables.utils.equiv_classes import EquivClasses
from transformation_algebra.transformation_algebra import TransformationAlgebra


def compare_states_cayley_tables(
    table1: CayleyTableStates, table2: CayleyTableStates
) -> tuple[bool, str]:
    """
    Compare two state Cayley tables for equality.

    Args:
        table1: First CayleyTableStates instance
        table2: Second CayleyTableStates instance

    Returns:
        tuple[bool, str]: (whether they match, detailed comparison message)
    """
    if table1 is None or table2 is None:
        return False, "One or both tables are None"

    # Check if tables have same number of elements
    elements1 = table1.get_row_labels()
    elements2 = table2.get_row_labels()
    if len(elements1) != len(elements2):
        return False, (
            f"Different number of elements: {len(elements1)} vs {len(elements2)}"
        )

    return table1.data == table2.data, "States Cayley tables are identical"


def compare_actions_cayley_tables(
    table1: CayleyTableActions, table2: CayleyTableActions
) -> tuple[bool, str]:
    """
    Compare two action Cayley tables for equality.

    Args:
        table1: First CayleyTableActions instance
        table2: Second CayleyTableActions instance

    Returns:
        tuple[bool, str]: (whether they match, detailed comparison message)
    """
    if table1 is None or table2 is None:
        return False, "One or both tables are None"

    # Check if tables have same number of elements
    elements1 = table1.get_all_actions()
    elements2 = table2.get_all_actions()
    if len(elements1) != len(elements2):
        return False, (
            f"Different number of elements: {len(elements1)} vs {len(elements2)}"
        )

    return table1.data == table2.data, "Actions Cayley tables are identical"


def compare_equiv_classes(
    equiv_classes1: EquivClasses, equiv_classes2: EquivClasses
) -> tuple[bool, str]:
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
        msg = "\nElements differ between equivalence classes:\n"
        if diff1:
            msg += f"- Elements only in first algebra: {sorted(diff1)}\n"
        if diff2:
            msg += f"- Elements only in second algebra: {sorted(diff2)}\n"
        return False, msg

    # Compare which elements are grouped together
    differences = []
    for element in all_elements1:
        class1 = equiv_classes1.get_element_class(element)
        class2 = equiv_classes2.get_element_class(element)

        if class1 is None or class2 is None:
            differences.append(f"Element '{element}' not found in one of the classes")
            continue

        elements1 = equiv_classes1.get_class_elements(class1)
        elements2 = equiv_classes2.get_class_elements(class2)

        if elements1 != elements2:
            differences.append(
                f"\nElement '{element}' belongs to different groups:\n"
                f"- In first algebra: {sorted(elements1)} (labeled as '{class1}')\n"
                f"- In second algebra: {sorted(elements2)} (labeled as '{class2}')"
            )

    if differences:
        msg = "Found differences in equivalence class groupings:\n" + "\n".join(
            differences
        )
        return False, msg

    return True, "Equivalence classes have same groupings but different labels"


def compare_algebras(
    algebra1: TransformationAlgebra, algebra2: TransformationAlgebra
) -> bool:
    """
    Compare two algebras to check if they are the same.

    Args:
        algebra1: First TransformationAlgebra instance
        algebra2: Second TransformationAlgebra instance

    Returns:
        bool: True if the algebras are the same, False otherwise
    """
    print(f"\nComparing algebras: {algebra1.name} vs {algebra2.name}")

    # Compare Cayley table states
    states_match, states_details = compare_states_cayley_tables(
        algebra1.cayley_table_states, algebra2.cayley_table_states
    )
    print(f"Cayley table states match: {states_match}")
    if not states_match:
        print(f"States table differences: {states_details}")

    # Compare Cayley table actions
    actions_match, actions_details = compare_actions_cayley_tables(
        algebra1.cayley_table_actions, algebra2.cayley_table_actions
    )
    print(f"Cayley table actions match: {actions_match}")
    if not actions_match:
        print(f"Actions table differences: {actions_details}")

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
