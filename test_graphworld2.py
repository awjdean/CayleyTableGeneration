from worlds.graphworlds.graphworld2_local_not_global_group import GraphWorld2


def main():
    # Create the graph world
    world = GraphWorld2()

    # Generate the transformation matrix (needed for drawing)
    world.generate_min_action_transformation_matrix()

    # Draw the graph
    world.draw_graph()


if __name__ == "__main__":
    main()
