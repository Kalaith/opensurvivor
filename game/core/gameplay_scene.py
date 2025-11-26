from __future__ import annotations

from typing import Any

from .scene_manager import Scene


class GameplayScene(Scene):
    """Scene that coordinates moment-to-moment gameplay systems.

    The scene delegates collision resolution, progression logic, and HUD updates
    to the injected systems. It stays lightweight so the tests can swap in
    fakes/mocks without pulling graphical dependencies.
    """

    def __init__(self, collision_system: Any, hud_system: Any, progression_system: Any):
        self.collision_system = collision_system
        self.hud_system = hud_system
        self.progression_system = progression_system

    def handle_input(self, *args, **kwargs) -> None:
        if hasattr(self.progression_system, "handle_input"):
            self.progression_system.handle_input(*args, **kwargs)

    def update(self, delta_time: float) -> None:
        # Collisions should run before progression to ensure the game state is
        # up-to-date for any downstream logic.
        self.collision_system.update(delta_time)
        self.progression_system.update(delta_time)

    def render(self, surface: Any | None = None) -> None:
        # Let the HUD know about the latest progression state before drawing.
        hud_context = None
        if hasattr(self.progression_system, "get_status"):
            hud_context = self.progression_system.get_status()
        self.hud_system.render(surface, hud_context)
