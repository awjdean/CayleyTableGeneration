import logging
import time
import weakref
from dataclasses import dataclass
from enum import Enum, auto

from cayley_tables.cayley_table_states import CayleyTableStates
from cayley_tables.equiv_classes import (
    EquivClasses,
    generate_initial_equivalence_classes,
)
from cayley_tables.states_cayley_table_generation.action_outcome import (
    generate_action_outcome,
)
from cayley_tables.states_cayley_table_generation.breaking_equiv_classes import (
    find_broken_equiv_classes,
)
from cayley_tables.states_cayley_table_generation.find_candidate_elements import (
    find_candidate_elements,
)
from cayley_tables.states_cayley_table_generation.initial_cayley_table_states import (
    generate_initial_cayley_table_states,
)
from utils.type_definitions import ActionType, StateType
from worlds.base_world import BaseWorld

PRINT_INTERVAL = 100
PROGRESS_LOG_INTERVAL = 5  # seconds

# Configure logging
logger = logging.getLogger(__name__)


class CayleyTableGenerationError(Exception):
    """Base exception for Cayley table generation errors."""

    pass


class GenerationState(Enum):
    """States of the generation process for debugging."""

    INITIALIZED = auto()
    GENERATING = auto()
    FINDING_CANDIDATES = auto()
    PROCESSING_BATCH = auto()
    COMPLETED = auto()
    FAILED = auto()


@dataclass
class DebugInfo:
    """Container for debug information."""

    last_candidate: str | None = None
    last_outcome: tuple | None = None
    last_error: Exception | None = None
    current_state: GenerationState = GenerationState.INITIALIZED


class CayleyTableGenerator:
    def __init__(
        self,
        world: BaseWorld,
        initial_state: StateType,
        log_level: int = logging.INFO,
        batch_size: int = 100,
        max_cache_size: int = 10000,
        debug_mode: bool = False,
    ) -> None:
        if not isinstance(world, BaseWorld):
            raise TypeError("world must be an instance of BaseWorld")
        if not world.get_min_actions():
            raise ValueError("World must have minimum actions defined")

        self.world: BaseWorld = world
        self.initial_state: StateType = initial_state
        self.min_actions: list[ActionType] = world.get_min_actions()
        self._validate_initial_state()

        self.equiv_classes: EquivClasses
        self.cayley_table_states: CayleyTableStates
        self.candidate_elements: set[ActionType] = set()
        self._stats = {
            "processed_candidates": 0,
            "class_breaks": 0,
            "added_to_existing": 0,
            "total_time": 0.0,
        }
        self._outcome_cache = {}

        # Configure instance logging
        self.logger: logging.Logger = logger
        self.logger.setLevel(log_level)
        self._batch_size: int = batch_size

        # Add progress tracking
        self._progress = {
            "total_candidates_found": 0,
            "total_batches": 0,
            "largest_batch": 0,
            "start_time": None,
            "last_progress_time": None,
        }

        # Memory management
        self._max_cache_size = max_cache_size
        self._cache_hits = 0
        self._cache_misses = 0
        self._outcome_cache: dict[tuple[ActionType, StateType], StateType] = {}

        # Use weak references where possible
        self._weak_world = weakref.proxy(world)

        # Debugging support
        self.debug_mode: bool = debug_mode
        self.debug_info = DebugInfo()

        if debug_mode:
            self.logger.setLevel(logging.DEBUG)

    def _validate_initial_state(self) -> None:
        """Validate the initial state."""
        try:
            possible_states = self.world.get_possible_states()
            if self.initial_state not in possible_states:
                raise ValueError(
                    f"Initial state {self.initial_state} not in possible states: "
                    f"{possible_states}"
                )
        except Exception as e:
            raise CayleyTableGenerationError(
                f"Failed to validate initial state: {e}"
            ) from e

    def generate(self) -> tuple[CayleyTableStates, EquivClasses]:
        """Main entry point with debugging support."""
        self._update_debug_info(GenerationState.GENERATING)
        self._progress["start_time"] = time.time()

        try:
            self._initialize_structures()

            while True:
                if not self._process_candidate_batch():
                    self._update_debug_info(GenerationState.FINDING_CANDIDATES)
                    if not self._find_new_candidates():
                        break
                self._log_progress()

            self._stats["total_time"] = time.time() - self._progress["start_time"]
            self._update_debug_info(GenerationState.COMPLETED)
            self._log_final_stats()
            return self.cayley_table_states, self.equiv_classes

        except Exception as e:
            self._update_debug_info(GenerationState.FAILED, error=e)
            self.logger.error(f"Generation failed: {e}", exc_info=True)
            raise

    def _process_candidate_batch(self, batch_size: int = 100) -> bool:
        """Process a batch of candidates for better performance."""
        if not self.candidate_elements:
            return False

        processed = 0
        while self.candidate_elements and processed < batch_size:
            candidate = self.candidate_elements.pop()
            self._process_single_candidate(candidate)
            processed += 1
            self._stats["processed_candidates"] += 1

        if processed > 0:
            print(
                f"\tProcessed {processed} candidates. {len(self.candidate_elements)}"
                " remaining."
            )
        return True

    def _process_single_candidate(self, candidate: ActionType) -> None:
        """Process a single candidate with debugging support."""
        if not isinstance(candidate, str):
            raise TypeError(f"Candidate must be a string, got {type(candidate)}")

        try:
            self._update_debug_info(
                GenerationState.PROCESSING_BATCH, candidate=candidate
            )

            # Check cache first
            cache_key = (candidate, self.initial_state)
            if cache_key in self._outcome_cache:
                if self._try_add_to_existing_class(candidate):
                    self._stats["added_to_existing"] += 1
                    return

            outcome = self._get_cached_outcome(candidate)
            self._update_debug_info(GenerationState.PROCESSING_BATCH, outcome=outcome)

            self._outcome_cache[cache_key] = outcome

            if self._try_add_to_existing_class(candidate):
                self._stats["added_to_existing"] += 1
                return

            self._handle_class_breaking(candidate)
            self._stats["class_breaks"] += 1

        except Exception as e:
            self._update_debug_info(GenerationState.FAILED, error=e)
            raise CayleyTableGenerationError(
                f"Error processing candidate {candidate}: {e}"
            ) from e

    def _get_cached_outcome(self, action: ActionType) -> StateType:
        """Get outcome from cache or compute it with memory management."""
        try:
            cache_key = (action, self.initial_state)

            if cache_key in self._outcome_cache:
                self._cache_hits += 1
                return self._outcome_cache[cache_key]

            self._cache_misses += 1
            outcome = generate_action_outcome(
                action=action, initial_state=self.initial_state, world=self._weak_world
            )

            self._outcome_cache[cache_key] = outcome
            self._manage_cache_size()

            return outcome

        except Exception as e:
            raise CayleyTableGenerationError(
                f"Failed to get outcome for action {action}: {e}"
            ) from e

    def _manage_cache_size(self) -> None:
        """Manage the outcome cache size to prevent memory issues."""
        if len(self._outcome_cache) > self._max_cache_size:
            items = list(self._outcome_cache.items())
            self._outcome_cache = dict(items[len(items) // 2 :])
            self.logger.debug(f"Cache cleaned. New size: {len(self._outcome_cache)}")

    def _initialize_structures(self) -> None:
        """Initialize the equivalence classes and Cayley table states."""
        self.equiv_classes = generate_initial_equivalence_classes(
            self.min_actions, self.initial_state, self.world
        )

        self.cayley_table_states = generate_initial_cayley_table_states(
            equiv_class_labels=self.equiv_classes.get_labels(),
            initial_state=self.initial_state,
            world=self.world,
        )
        print("\tInitial Cayley table generated.")

    def _try_add_to_existing_class(self, candidate: ActionType) -> bool:
        """Try to add candidate to an existing equivalence class."""
        equiv_elements = self.cayley_table_states.find_equiv_elements(
            element=candidate,
            initial_state=self.initial_state,
            world=self.world,
            take_first=True,
        )

        if equiv_elements:
            equiv_element_label = next(iter(equiv_elements.keys()))
            self.equiv_classes.add_element(
                element=candidate, class_label=equiv_element_label
            )
            return True
        return False

    def _handle_class_breaking(self, candidate: ActionType) -> None:
        """Handle the case where a candidate breaks existing classes."""
        new_equiv_classes = find_broken_equiv_classes(
            candidate_element=candidate,
            equiv_classes=self.equiv_classes,
            initial_state=self.initial_state,
            world=self.world,
        )

        if len(new_equiv_classes.data) != 0:
            print(f"\t{candidate} split classes:\n\t{new_equiv_classes.data}")

        self._update_structures(candidate, new_equiv_classes)

    def _update_structures(
        self, candidate: ActionType, new_equiv_classes: EquivClasses
    ) -> None:
        """Update the equivalence classes and Cayley table with new classes."""
        if not isinstance(new_equiv_classes, EquivClasses):
            raise TypeError(
                f"new_equiv_classes must be EquivClasses, got {type(new_equiv_classes)}"
            )

        try:
            self.equiv_classes.remove_elements_from_classes(
                new_equiv_classes.get_all_elements()
            )

            new_equiv_classes.create_new_class(
                class_label=candidate,
                outcome=self._get_cached_outcome(candidate),
                elements=[candidate],
            )

            self.equiv_classes.merge_equiv_class_instances(new_equiv_classes)
            self.cayley_table_states.add_equiv_classes(
                new_equiv_classes, self.initial_state, self.world
            )
        except Exception as e:
            raise CayleyTableGenerationError(
                f"Failed to update structures with candidate {candidate}: {e}"
            ) from e

    def _find_new_candidates(self) -> bool:
        """Find new candidate elements to process."""
        self.logger.info("\nSearching for new candidate elements")
        start_time = time.time()

        try:
            self.candidate_elements = find_candidate_elements(
                cayley_table_states=self.cayley_table_states,
                initial_state=self.initial_state,
                world=self.world,
                equiv_classes=self.equiv_classes,
            )

            count = len(self.candidate_elements)
            self._progress["total_candidates_found"] += count
            self._progress["largest_batch"] = max(
                self._progress["largest_batch"], count
            )

            elapsed_time = time.time() - start_time
            self.logger.info(f"Found {count} new candidates (in {elapsed_time:.2f}s)")

            return bool(self.candidate_elements)

        except Exception as e:
            self.logger.error("Failed to find new candidates", exc_info=True)
            raise CayleyTableGenerationError(
                f"Failed to find new candidates: {e}"
            ) from e

    def _log_progress(self) -> None:
        """Log progress information periodically."""
        current_time = time.time()
        if (
            self._progress["last_progress_time"] is None
            or current_time - self._progress["last_progress_time"]
            >= PROGRESS_LOG_INTERVAL
        ):
            elapsed = current_time - self._progress["start_time"]
            rate = self._stats["processed_candidates"] / elapsed if elapsed > 0 else 0

            self.logger.info(
                f"Progress: {self._stats['processed_candidates']} candidates processed "
                f"({rate:.1f}/s). {len(self.candidate_elements)} remaining. "
                f"Classes broken: {self._stats['class_breaks']}"
            )
            self._progress["last_progress_time"] = current_time

    def _log_final_stats(self) -> None:
        """Log final statistics with memory usage information."""
        self.logger.info("\nGeneration completed successfully")
        self.logger.info("Final Statistics:")
        self.logger.info(
            f"Total candidates processed: {self._stats['processed_candidates']}"
        )
        self.logger.info(
            f"Candidates added to existing classes: {self._stats['added_to_existing']}"
        )
        self.logger.info(f"Classes broken: {self._stats['class_breaks']}")
        self.logger.info(f"Total time: {self._stats['total_time']:.2f} seconds")
        self.logger.info(f"Cache entries: {len(self._outcome_cache)}")

        # Calculate additional statistics
        avg_rate = (
            self._stats["processed_candidates"] / self._stats["total_time"]
            if self._stats["total_time"] > 0
            else 0
        )
        self.logger.info(f"Average processing rate: {avg_rate:.1f} candidates/second")

        # Add memory statistics
        cache_total = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / cache_total * 100) if cache_total > 0 else 0

        self.logger.info("\nMemory Statistics:")
        self.logger.info(f"Cache size: {len(self._outcome_cache)} entries")
        self.logger.info(f"Cache hits: {self._cache_hits}")
        self.logger.info(f"Cache misses: {self._cache_misses}")
        self.logger.info(f"Cache hit rate: {hit_rate:.1f}%")

    def _update_debug_info(
        self,
        state: GenerationState,
        candidate: str | None = None,
        outcome: tuple | None = None,
        error: Exception | None = None,
    ) -> None:
        """Update debug information."""
        if not self.debug_mode:
            return

        self.debug_info.current_state = state
        if candidate is not None:
            self.debug_info.last_candidate = candidate
        if outcome is not None:
            self.debug_info.last_outcome = outcome
        if error is not None:
            self.debug_info.last_error = error

        self.logger.debug(
            f"Debug state: {state.name}, "
            f"Candidate: {self.debug_info.last_candidate}, "
            f"Outcome: {self.debug_info.last_outcome}"
        )

    def get_debug_snapshot(self) -> dict:
        """Get a snapshot of the current state for debugging."""
        if not self.debug_mode:
            return {}

        return {
            "debug_info": self.debug_info,
            "stats": self._stats.copy(),
            "progress": self._progress.copy(),
            "cache_info": {
                "size": len(self._outcome_cache),
                "hits": self._cache_hits,
                "misses": self._cache_misses,
            },
            "structures": {
                "equiv_classes_size": len(self.equiv_classes.data)
                if self.equiv_classes
                else 0,
                "cayley_table_size": len(self.cayley_table_states.data)
                if self.cayley_table_states
                else 0,
                "candidates_remaining": len(self.candidate_elements),
            },
        }
