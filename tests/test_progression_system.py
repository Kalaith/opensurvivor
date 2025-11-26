from game.systems.progression import ProgressionState, ProgressionSystem


CHARACTERS = {
    "square": {"unlock": None},
    "triangle": {"unlock": {"character": "square", "seconds": 600}},
    "circle": {"unlock": {"character": "triangle", "seconds": 600}},
}


def test_start_run_resets_timer_and_current_character():
    state = ProgressionState(elapsed_time=25.0, last_score=15.0, current_character="square")
    system = ProgressionSystem(CHARACTERS)

    system.start_run(state, character_key="triangle")

    assert state.current_character == "triangle"
    assert state.elapsed_time == 0.0
    assert state.last_score == 0.0
    assert state.best_survival_times["triangle"] == 0.0


def test_record_game_over_updates_bests_and_unlocks():
    state = ProgressionState(elapsed_time=620.0, current_character="square")
    system = ProgressionSystem(CHARACTERS)

    system.record_game_over(state)

    assert state.last_score == 620.0
    assert state.best_survival_times["square"] == 620.0
    assert "triangle" in state.unlocked_characters
