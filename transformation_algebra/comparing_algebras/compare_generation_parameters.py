from transformation_algebra.transformation_algebra import TransformationAlgebra


def compare_generation_parameters(
    algebra1: TransformationAlgebra, algebra2: TransformationAlgebra
) -> tuple[bool, str]:
    """
    Compare the generation parameters of two transformation algebras.

    Args:
        algebra1: First TransformationAlgebra instance
        algebra2: Second TransformationAlgebra instance

    Returns:
        Tuple[bool, str]: (whether parameters match, detailed comparison message)
    """
    params1 = algebra1._algebra_generation_parameters
    params2 = algebra2._algebra_generation_parameters

    if params1 is None or params2 is None:
        return False, "One or both algebras have no generation parameters"

    differences = []

    # Compare world parameters
    world1 = params1.get("world")
    world2 = params2.get("world")

    if world1.__class__ != world2.__class__:
        differences.append(
            f"World types differ: {world1.__class__.__name__} vs"
            f" {world2.__class__.__name__}"
        )
    else:
        # Compare world attributes that affect algebra generation
        world_attrs_to_check = [
            "_MIN_ACTIONS",
            "_possible_states",
            "_min_action_transformation_matrix",
        ]
        for attr in world_attrs_to_check:
            val1 = getattr(world1, attr, None)
            val2 = getattr(world2, attr, None)
            if val1 != val2:
                differences.append(
                    f"World {attr} differs:\n"
                    f"- First algebra: {val1}\n"
                    f"- Second algebra: {val2}"
                )

    # Compare initial states
    initial_state1 = params1.get("initial_state")
    initial_state2 = params2.get("initial_state")
    if initial_state1 != initial_state2:
        differences.append(
            f"Initial states differ:\n"
            f"- First algebra: {initial_state1}\n"
            f"- Second algebra: {initial_state2}"
        )

    # Compare any additional parameters
    all_keys = set(params1.keys()) | set(params2.keys())
    for key in all_keys:
        if key not in ["world", "initial_state"]:  # Skip already compared params
            val1 = params1.get(key)
            val2 = params2.get(key)
            if val1 != val2:
                differences.append(
                    f"Parameter '{key}' differs:\n"
                    f"- First algebra: {val1}\n"
                    f"- Second algebra: {val2}"
                )

    if differences:
        msg = "Generation parameters differ:\n" + "\n".join(differences)
        return False, msg

    return True, "Generation parameters are identical"


def main():
    """Example usage of the comparison function."""
    # Example usage
    algebra1_name = "gridworld_2x2_wall_2"
    algebra2_name = "gridworld_2x2_wall_3"

    # Load algebras
    print("\nLoading algebras...")
    algebra1 = TransformationAlgebra(name=algebra1_name)
    algebra1.load()

    algebra2 = TransformationAlgebra(name=algebra2_name)
    algebra2.load()

    # Compare parameters
    match, details = compare_generation_parameters(algebra1, algebra2)
    print(f"\nParameters match: {match}")
    if not match:
        print("\nDetails:")
        print(details)


if __name__ == "__main__":
    main()
