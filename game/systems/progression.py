from dataclasses import dataclass, field
from typing import Mapping


@dataclass
class ProgressionState:
    """Mutable snapshot of player progression during and between runs."""

    elapsed_time: float = 0.0
    last_score: float = 0.0
    current_character: str | None = None
    best_survival_times: dict[str, float] = field(
        default_factory=lambda: {"square": 0.0, "triangle": 0.0, "circle": 0.0}
    )
    unlocked_characters: set[str] = field(default_factory=lambda: {"square"})


class ProgressionSystem:
    """Track survival progress and unlock new characters based on performance."""

    def __init__(self, character_definitions: Mapping[str, Mapping]):
        self.character_definitions = character_definitions

    def start_run(self, state: ProgressionState, *, character_key: str) -> None:
        """Initialize a new run for the chosen character."""
        state.current_character = character_key
        state.elapsed_time = 0.0
        state.last_score = 0.0
        state.best_survival_times.setdefault(character_key, 0.0)

    def update(
        self,
        state: ProgressionState,
        delta_time: float,
        *,
        player_alive: bool,
    ) -> None:
        """Advance survival timers and unlocks during active gameplay."""
        if player_alive:
            state.elapsed_time += delta_time

        self.record_personal_best(state)
        self.unlock_rewards(state)

    def record_personal_best(self, state: ProgressionState) -> None:
        if not state.current_character:
            return

        best = state.best_survival_times.get(state.current_character, 0.0)
        if state.elapsed_time > best:
            state.best_survival_times[state.current_character] = state.elapsed_time

    def record_game_over(self, state: ProgressionState) -> None:
        """Finalize score and unlocks after the player is defeated."""
        state.last_score = state.elapsed_time
        self.record_personal_best(state)
        self.unlock_rewards(state)

    def unlock_rewards(self, state: ProgressionState) -> None:
        """Grant characters whose prerequisites have been met."""
        for key, definition in self.character_definitions.items():
            unlock = definition.get("unlock")
            state.best_survival_times.setdefault(key, 0.0)
            if not unlock:
                state.unlocked_characters.add(key)
                continue

            prerequisite = unlock.get("character")
            requirement = unlock.get("seconds", 0)
            if state.best_survival_times.get(prerequisite, 0.0) >= requirement:
                state.unlocked_characters.add(key)
