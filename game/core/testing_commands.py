from __future__ import annotations

import arcade


class TestingCommandHandler:
    """Developer/testing hotkeys for quickly manipulating progression.

    All commands require holding both CTRL and SHIFT to avoid accidental
    activation during normal play.
    """

    __test__ = False

    def __init__(self, engine):
        self.engine = engine
        self._command_map = {
            arcade.key.F10: self._skip_run_10_minutes,
            arcade.key.KEY_1: lambda: self._set_best_time("square"),
            arcade.key.KEY_2: lambda: self._set_best_time("triangle"),
            arcade.key.KEY_3: lambda: self._set_best_time("circle"),
        }
        f11_key = getattr(arcade.key, "F11", None)
        if f11_key is not None:
            self._command_map[f11_key] = self._toggle_invincible_overwhelm

    def handle_key_press(self, key, modifiers) -> bool:
        """Execute a testing command if its hotkey is pressed.

        Returns True when a command handled the input so the rest of the
        input pipeline can be skipped.
        """

        if not (modifiers & arcade.key.MOD_CTRL and modifiers & arcade.key.MOD_SHIFT):
            return False

        handler = self._command_map.get(key)
        if not handler:
            return False

        handler()
        return True

    def _skip_run_10_minutes(self) -> None:
        """Fast-forward the active run timer by 10 minutes for testing."""

        if self.engine.state != "playing":
            return

        self.engine.elapsed_time += 600.0
        self.engine.update_unlocks()

    def _set_best_time(self, character_key: str) -> None:
        """Mark a character as having survived 10 minutes to unlock dependents."""

        best_times = self.engine.progression_state.best_survival_times
        previous_best = best_times.get(character_key, 0.0)
        if previous_best >= 600.0:
            return

        best_times[character_key] = 600.0
        self.engine.progression_system.unlock_rewards(self.engine.progression_state)

    def _toggle_invincible_overwhelm(self) -> None:
        """Toggle player invincibility and crank spawns for stress testing."""

        if self.engine.state != "playing" or not getattr(self.engine, "player", None):
            return

        player = self.engine.player
        player.invincible = not player.invincible
        print(f"Invincibility {'ENABLED' if player.invincible else 'DISABLED'}")

        if player.invincible and getattr(self.engine, "spawning_system", None):
            self.engine.spawning_system.overwhelm_mode = True
        elif getattr(self.engine, "spawning_system", None):
            self.engine.spawning_system.overwhelm_mode = False
