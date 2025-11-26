import arcade

from game.core.testing_commands import TestingCommandHandler
from game.systems.progression import ProgressionState, ProgressionSystem


CHARACTERS = {
    "square": {"unlock": None},
    "triangle": {"unlock": {"character": "square", "seconds": 600}},
    "circle": {"unlock": {"character": "triangle", "seconds": 600}},
}


class DummyEngine:
    def __init__(self):
        self.state = "playing"
        self.progression_state = ProgressionState(current_character="square")
        self.progression_system = ProgressionSystem(CHARACTERS)

    @property
    def elapsed_time(self):
        return self.progression_state.elapsed_time

    @elapsed_time.setter
    def elapsed_time(self, value: float):
        self.progression_state.elapsed_time = value

    def update_unlocks(self) -> None:
        self.progression_state.elapsed_time = self.elapsed_time
        self.progression_system.record_personal_best(self.progression_state)
        self.progression_system.unlock_rewards(self.progression_state)


def test_skip_run_10_minutes_advances_timer_and_unlocks():
    engine = DummyEngine()
    handler = TestingCommandHandler(engine)

    handled = handler.handle_key_press(
        arcade.key.F10, arcade.key.MOD_CTRL | arcade.key.MOD_SHIFT
    )

    assert handled is True
    assert engine.elapsed_time == 600.0
    assert engine.progression_state.best_survival_times["square"] == 600.0
    assert "triangle" in engine.progression_state.unlocked_characters


def test_missing_modifiers_does_not_trigger_commands():
    engine = DummyEngine()
    handler = TestingCommandHandler(engine)

    handled = handler.handle_key_press(arcade.key.KEY_1, modifiers=0)

    assert handled is False
    assert engine.progression_state.best_survival_times["square"] == 0.0
