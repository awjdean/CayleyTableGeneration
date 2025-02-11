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
  - Replace action sequence strings with tuples (like pseudocode).
- Restructure code to sepearate out the two different generation algorithms.
  - Split equiv_classes into multiple classes that inherit.
    - For new generation version: no outcome; ability to sort elements into equivalence classes by calculating their action_functions.
  - Reorganise directories.
- Function that compares actions Cayley tables for the two methods.
- Turn action_functions into a typed dict ?
- Sort elements in new generation method.
- New generation method, actions Cayley table: Check if elements in equiv_classes (if so, can fill table entry with class label), and add elements to relevant equiv_class if not in one.
- New generation method:
  - Hashing action functions might speed lookups.
- Sort inheritance for generators of local vs method 2.
  - Create base classes with shared methods + variables.
- Directory refactor.
- Simplify imports using init.py files ?
- Comparison between actions Cayley tables generated using the two methods.

# Smaller things

- Change states set up so it's always ((agent_x, agent_y,...), (positions of other things),...).
- Fix saving for worlds --> put in Saving class and inherit ?
- Function to return number of elements in Cayley table.
- Print number of elements in Cayley table.
- Make properties tables print like in thesis.
- No outcome in EquivClasses if action functions method used.
  - Or write function that gets the outcomes that can be used for the old method ?

# Maybe things

- Json saving --> prevents annoying pickle issues (e.g., import issues).
- Include a max time estimate for states Cayley table generation ?
