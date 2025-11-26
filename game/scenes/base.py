from __future__ import annotations

from typing import Protocol


class BaseScene(Protocol):
    """Common interface for engine-driven scenes."""

    def on_enter(self) -> None:
        """Hook called when the scene becomes active."""

    def on_exit(self) -> None:
        """Hook called when the scene is replaced."""

    def update(self, delta_time: float) -> None:
        """Advance the scene by ``delta_time`` seconds."""

    def render(self) -> None:
        """Draw the scene contents to the window surface."""

    def handle_key_press(self, key, modifiers) -> None:
        """Handle a key press event."""

    def handle_key_release(self, key, modifiers) -> None:
        """Handle a key release event."""

    def handle_mouse_motion(self, x: float, y: float, dx: float, dy: float) -> None:
        """Handle mouse motion events."""

    def handle_mouse_press(self, x: float, y: float, button, modifiers) -> None:
        """Handle mouse press events."""
