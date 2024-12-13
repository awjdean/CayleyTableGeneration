import logging
import time

from cayley_tables.tables.cayley_table_states import CayleyTableStates
from cayley_tables.utils.action_outcome import generate_action_outcome
from cayley_tables.utils.equiv_classes import (
    EquivClasses,
)
from utils.type_definitions import ActionType, StateType
from worlds.base_world import BaseWorld

PROGRESS_LOG_INTERVAL = 10  # seconds
logger = logging.getLogger(__name__)


class StatesCayleyTableGenerator:
    """
    Generates Cayley table states and equivalence classes for a world's transformations.

    This class builds a complete transformation algebra by:
    1. Starting with minimal actions from the world
    2. Finding new candidate elements by composing existing elements
    3. Testing if candidates belong to existing classes or break them
    4. Iterating until no new candidates are found

    Attributes:
        world: The world whose transformations we're analyzing
        initial_state: Starting state for applying transformations
        min_actions: Minimal set of actions from the world
        equiv_classes: Current equivalence classes of transformations
        cayley_table_states: Current Cayley table mapping actions to states
        candidate_elements: Set of action sequences to process
    """

    # --------------------------------------------------------------------------
    # Setup and Main Entry
    # --------------------------------------------------------------------------
    def __init__(
        self, world: BaseWorld, initial_state: StateType, log_level: int = logging.INFO
    ) -> None:
        """
        Initialize the generator with a world and starting state.

        Args:
            world: World whose transformations we're analyzing
            initial_state: State from which to start applying transformations
            log_level: Logging level for progress updates

        Raises:
            ValueError: If world has no minimum actions defined
        """
        # Core state
        self.world = world
        self.initial_state = initial_state
        self.min_actions = world.get_min_actions()
        if not self.min_actions:
            raise ValueError("World must have minimum actions defined")

        # Generation structures
        self.equiv_classes: EquivClasses
        self.cayley_table_states: CayleyTableStates
        self.candidate_elements: set[ActionType] = set()

        # Stats and logging
        self.logger = logger
        self.logger.setLevel(log_level)
        self._stats = {"processed": 0, "breaks": 0, "added": 0, "time": 0.0}
        self._last_log_time: float | None = None
        self._start_time: float

    def generate(self) -> tuple[CayleyTableStates, EquivClasses]:
        """
        Generate the complete Cayley table and equivalence classes.

        The main algorithm:
        1. Initialize structures with minimal actions
        2. Find candidate elements by composing existing elements
        3. Process candidates to find new equivalence classes
        4. Repeat until no new candidates are found

        Returns:
            tuple[CayleyTableStates, EquivClasses]:
                - The completed Cayley table of states
                - The final equivalence classes

        Raises:
            Exception: If generation fails for any reason
        """
        self._start_time = time.time()

        try:
            self._initialize_structures()

            while True:
                if not self._find_new_candidates():
                    break

                while self.candidate_elements:
                    candidate = self.candidate_elements.pop()
                    self._process_candidate(candidate)
                    self._stats["processed"] += 1
                    self._log_progress()

            self._stats["time"] = time.time() - self._start_time
            self._log_final_stats()
            return self.cayley_table_states, self.equiv_classes

        except Exception as e:
            self.logger.error(f"Generation failed: {e}", exc_info=True)
            raise

    # --------------------------------------------------------------------------
    # Initial Structure Generation
    # --------------------------------------------------------------------------
    def _initialize_structures(self) -> None:
        """
        Initialize the equivalence classes and Cayley table states.

        Creates the initial structures:
        1. Generates equivalence classes from minimal actions
        2. Creates initial Cayley table from these classes
        """
        self.equiv_classes = self._generate_initial_equivalence_classes()
        self.cayley_table_states = self._generate_initial_cayley_table_states()
        print("\tInitial Cayley table generated.")

    def _generate_initial_equivalence_classes(self) -> EquivClasses:
        """
        Creates initial equivalence classes based on the minimum actions
        and the initial state of the world.

        This method iterates through the minimum actions and generates the
        corresponding outcomes for each action. It then compares these outcomes
        with the existing equivalence classes to determine if the action can be
        added to an existing class or if a new class needs to be created.

        Returns:
            EquivalenceClasses: An instance of EquivalenceClasses containing
                               the newly created equivalence classes based on
                               the evaluated actions and their outcomes.
        """
        equiv_classes = EquivClasses()
        for a in self.min_actions:
            # Calculate: \hat{a} * w_{0}.
            a_outcome = generate_action_outcome(
                action=a, initial_state=self.initial_state, world=self.world
            )
            for b in equiv_classes.get_labels():
                # Calculate: b * w_{0}.
                b_outcome = equiv_classes.get_class_outcome(class_label=b)
                if a_outcome == b_outcome:
                    equiv_classes.add_element(element=a, class_label=b)
                    break
            else:
                equiv_classes.create_new_class(
                    class_label=a, outcome=a_outcome, elements=[a]
                )

        return equiv_classes

    def _generate_initial_cayley_table_states(self) -> CayleyTableStates:
        """
        Generate the initial Cayley table from minimal actions.

        Creates a table where:
        - Rows and columns are labeled by equivalence class labels
        - Each cell contains the outcome state of composing those actions

        Returns:
            CayleyTableStates: The initial Cayley table mapping actions to outcome
              states
        """
        cayley_table_states = CayleyTableStates()
        labels = self.equiv_classes.get_labels()

        for row_label in labels:
            cayley_table_states.data[row_label] = {}
            for col_label in labels:
                action = col_label + row_label
                outcome = generate_action_outcome(
                    action=action,
                    initial_state=self.initial_state,
                    world=self.world,
                )
                cayley_table_states.data[row_label][col_label] = outcome
        return cayley_table_states

    # --------------------------------------------------------------------------
    # Candidate Finding and Processing
    # --------------------------------------------------------------------------
    def _find_new_candidates(self) -> bool:
        """
        Search for and collect new candidate elements.

        Looks for new candidates by examining all possible compositions
        of existing elements in the Cayley table.

        Returns:
            bool: True if new candidates were found, False otherwise

        Raises:
            ValueError: If candidate finding process fails
        """
        self.logger.info("\nSearching for new candidate elements")
        start = time.time()

        try:
            self.candidate_elements = (
                self._find_candidate_elements_in_states_cayley_table()
            )
            count = len(self.candidate_elements)

            elapsed = time.time() - start
            self.logger.info(f"Found {count} new candidates (in {elapsed:.2f}s)")
            return bool(self.candidate_elements)

        except Exception as e:
            self.logger.error("Failed to find new candidates", exc_info=True)
            raise ValueError(f"Failed to find new candidates: {e}") from e

    def _find_candidate_elements_in_states_cayley_table(self) -> set[ActionType]:
        """
        Find new candidate elements by examining the Cayley table.

        For each pair of elements in the table:
        1. Composes them to create a potential candidate
        2. Checks if it belongs to an existing class
        3. Adds it to candidates if it's new

        Returns:
            set[ActionType]: Set of new candidate action sequences

        Raises:
            ValueError: If a candidate belongs to multiple classes
        """
        candidates = set()
        for row_label in self.cayley_table_states.get_row_labels():
            for col_label in self.cayley_table_states.get_row_labels():
                candidate = col_label + row_label
                equiv_elements = self.cayley_table_states.find_equiv_elements(
                    element=candidate,
                    initial_state=self.initial_state,
                    world=self.world,
                )

                if len(equiv_elements) == 1:
                    label = next(iter(equiv_elements.keys()))
                    self.equiv_classes.add_element(element=candidate, class_label=label)
                elif len(equiv_elements) == 0:
                    candidates.add(candidate)
                else:
                    raise ValueError(
                        "Candidate element is in multiple equivalence classes."
                    )
        return candidates

    def _process_candidate(self, candidate: ActionType) -> None:
        """
        Process a single candidate element.

        Attempts to either:
        1. Add the candidate to an existing equivalence class
        2. Use it to break existing classes if it distinguishes elements

        Args:
            candidate: The action sequence to process

        Raises:
            ValueError: If processing the candidate fails
        """
        try:
            if self._try_add_to_existing_class(candidate):
                self._stats["added"] += 1
                return

            self._handle_class_breaking(candidate)
            self._stats["breaks"] += 1

        except Exception as e:
            raise ValueError(f"Error processing candidate {candidate}: {e}") from e

    def _try_add_to_existing_class(self, candidate: ActionType) -> bool:
        """
        Try to add candidate to an existing equivalence class.

        Checks if the candidate's behavior matches any existing class.
        If so, adds it to that class.

        Args:
            candidate: The action sequence to try adding

        Returns:
            bool: True if added to existing class, False if needs new class
        """
        equiv_elements = self.cayley_table_states.find_equiv_elements(
            element=candidate,
            initial_state=self.initial_state,
            world=self.world,
            take_first=True,
        )

        if equiv_elements:
            label = next(iter(equiv_elements.keys()))
            self.equiv_classes.add_element(element=candidate, class_label=label)
            return True
        return False

    # --------------------------------------------------------------------------
    # Class Breaking
    # --------------------------------------------------------------------------
    def _handle_class_breaking(self, candidate: ActionType) -> None:
        """
        Handle a candidate that breaks existing equivalence classes.

        When a candidate distinguishes elements that were thought equivalent,
        this splits the affected classes and updates all related structures.

        Args:
            candidate: The action sequence that breaks classes
        """
        new_classes = self._find_broken_equiv_classes(candidate)

        if new_classes.data:
            print(f"\t{candidate} split classes:\n\t{new_classes.data}")

        self._update_structures(candidate, new_classes)

    def _find_broken_equiv_classes(self, candidate_element: ActionType) -> EquivClasses:
        """
        Find equivalence classes that are broken by a candidate element.

        A class is broken when the candidate element shows that elements
        previously thought equivalent actually behave differently.

        Args:
            candidate_element: Action sequence that might break classes

        Returns:
            EquivClasses: New equivalence classes created by breaking
        """
        new_equiv_classes = EquivClasses()
        for class_label in self.equiv_classes.get_labels():
            # Check if candidate_element breaks the equiv class labelled by class_label.
            temp_new_equivs = self._check_if_equiv_class_broken(
                candidate_element=candidate_element,
                b_label=class_label,
            )
            new_equiv_classes.merge_equiv_class_instances(temp_new_equivs)

        return new_equiv_classes

    def _check_if_equiv_class_broken(
        self, candidate_element: ActionType, b_label: ActionType
    ) -> EquivClasses:
        """
        Check if a candidate breaks a specific equivalence class.

        Args:
            candidate_element: Action sequence to test
            b_label: Label of equivalence class to check

        Returns:
            EquivClasses: New classes if broken, empty if not
        """
        new_equiv_classes = EquivClasses()
        if len(self.equiv_classes.get_class_elements(b_label)) == 1:
            return new_equiv_classes

        # Calculate: b_label * (candidate_element * w_{0}).
        b_label_outcome = generate_action_outcome(
            action=b_label + candidate_element,
            initial_state=self.initial_state,
            world=self.world,
        )

        for b_element in self.equiv_classes.get_class_elements(b_label):
            # Calculate: b_element * (candidate_element * w_{0}).
            b_element_outcome = generate_action_outcome(
                action=b_element + candidate_element,
                initial_state=self.initial_state,
                world=self.world,
            )
            # If b_label * (candidate_element * w_{0}) != b_element * (candidate_element
            # * w_{0}), then b_element should be in a different equiv class to b_label
            # (candidate_element has broken the equiv class labelled by b_label).
            if b_label_outcome != b_element_outcome:
                for c_label in new_equiv_classes.get_labels():
                    # Calculate: c_label * (candidate_element * w_{0}).
                    c_outcome = generate_action_outcome(
                        action=c_label + candidate_element,
                        initial_state=self.initial_state,
                        world=self.world,
                    )

                    # If b_element * (candidate_element * w_{0}) = c_label *
                    # (candidate_element * w_{0}), then b_element is in b_element's
                    #  equiv class.
                    if b_element_outcome == c_outcome:
                        new_equiv_classes.add_element(
                            element=b_element, class_label=c_label
                        )
                        break
                # If b_element not in any existing new equiv class, then create new
                #  equiv class with b_element as label.
                else:
                    # TODO: double check this.
                    new_equiv_outcome = self.equiv_classes.get_class_outcome(b_label)
                    new_equiv_classes.create_new_class(
                        class_label=b_element,
                        outcome=new_equiv_outcome,
                        elements=[b_element],
                    )
        return new_equiv_classes

    def _update_structures(
        self, candidate: ActionType, new_classes: EquivClasses
    ) -> None:
        """
        Update data structures after breaking equivalence classes.

        Steps:
        1. Removes elements from their old classes
        2. Creates a new class for the candidate
        3. Merges the new class structure
        4. Updates the Cayley table

        Args:
            candidate: The action sequence that caused the break
            new_classes: The new equivalence class structure

        Raises:
            ValueError: If updating the structures fails
        """
        try:
            # Remove elements that will be in new classes
            self.equiv_classes.remove_elements_from_classes(
                new_classes.get_all_elements()
            )

            # Create new class for candidate
            outcome = generate_action_outcome(
                action=candidate, initial_state=self.initial_state, world=self.world
            )
            new_classes.create_new_class(
                class_label=candidate,
                outcome=outcome,
                elements=[candidate],
            )

            # Update structures
            self.equiv_classes.merge_equiv_class_instances(new_classes)
            self.cayley_table_states.add_equiv_classes(
                new_classes, self.initial_state, self.world
            )
        except Exception as e:
            raise ValueError(f"Failed to update structures: {e}") from e

    # --------------------------------------------------------------------------
    # Support Methods
    # --------------------------------------------------------------------------
    def _log_progress(self) -> None:
        """
        Log progress information periodically.

        Logs statistics about:
        - Number of candidates processed
        - Processing rate
        - Remaining candidates
        - Number of classes broken

        Only logs if PROGRESS_LOG_INTERVAL seconds have passed since last log.
        """
        current_time = time.time()
        if (
            self._last_log_time is None
            or current_time - self._last_log_time >= PROGRESS_LOG_INTERVAL
        ):
            elapsed = current_time - self._start_time
            rate = self._stats["processed"] / elapsed if elapsed > 0 else 0

            self.logger.info(
                f"Progress: Processed {self._stats['processed']} candidates "
                f"({rate:.1f}/s). Remaining: {len(self.candidate_elements)}. "
                f"Classes broken: {self._stats['breaks']}"
            )
            self._last_log_time = current_time

    def _log_final_stats(self) -> None:
        """
        Log final statistics about the generation process.

        Logs:
        - Total candidates processed
        - Candidates added to existing classes
        - Number of classes broken
        - Total processing time
        - Average processing rate
        """
        self.logger.info("\nGeneration completed successfully")
        self.logger.info("Final Statistics:")
        self.logger.info(f"Total candidates processed: {self._stats['processed']}")
        self.logger.info(f"Candidates added to existing: {self._stats['added']}")
        self.logger.info(f"Classes broken: {self._stats['breaks']}")
        self.logger.info(f"Total time: {self._stats['time']:.2f} seconds")

        rate = (
            self._stats["processed"] / self._stats["time"]
            if self._stats["time"] > 0
            else 0
        )
        self.logger.info(f"Average processing rate: {rate:.1f} candidates/second")
