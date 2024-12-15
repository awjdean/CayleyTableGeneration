# Important

- Write readme.
- Set up all experiments in thesis in a launch.json equivalent.
- Fix issues with world_saver.

# Bigger things

- Make all gridworld_2d classes inherit from gridworld_2d.
  - Append additional min_actions in relevant classes (e.g., consume action).
- Function that reduces action sequences down to a class labelling element.
- States Cayley table checkers:
  - Check there are no elements in more than one equivalence class.
  - Check each processed element has the same state Cayley row and state Cayley column as its class labelling element.
- Make code structure match pseudocode structure.

# Smaller things

- Change states set up so it's always ((agent_x, agent_y,...), (positions of other things),...).
- Fix saving for worlds --> put in Saving class and inherit ?

# Maybe things

- Json saving --> prevents annoying pickle issues (e.g., import issues).
- Include a max time estimate for states Cayley table generation ?
