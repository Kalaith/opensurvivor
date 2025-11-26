from __future__ import annotations

from typing import Optional


class Scene:
    """Base class for all scenes used by :class:`SceneManager`.

    Scenes can override lifecycle hooks and the main loop callbacks. The base
    implementations are intentionally no-ops so subclasses only implement what
    they need during tests.
    """

    def on_enter(self) -> None:
        """Called when the scene becomes the active scene."""

    def on_exit(self) -> None:
        """Called when the scene is replaced by another scene."""

    def handle_input(self, *args, **kwargs) -> None:
        """Process input forwarded by the owning engine or window."""

    def update(self, *args, **kwargs) -> None:
        """Advance the scene simulation."""

    def render(self, *args, **kwargs) -> None:
        """Draw the scene contents to the active surface."""


class SceneManager:
    """Minimal scene manager coordinating lifecycle and delegation.

    The manager keeps a reference to the current scene and exposes methods the
    engine can call from its event hooks. It handles calling ``on_exit`` on the
    outgoing scene and ``on_enter`` on the incoming one, and proxies
    ``handle_input``, ``update`` and ``render`` to whichever scene is active.
    """

    def __init__(self) -> None:
        self.current_scene: Optional[Scene] = None

    def switch_to(self, scene: Scene) -> None:
        if self.current_scene is scene:
            return
        if self.current_scene:
            self.current_scene.on_exit()
        self.current_scene = scene
        if self.current_scene:
            self.current_scene.on_enter()

    def handle_input(self, *args, **kwargs) -> None:
        if self.current_scene:
            self.current_scene.handle_input(*args, **kwargs)

    def update(self, *args, **kwargs) -> None:
        if self.current_scene:
            self.current_scene.update(*args, **kwargs)

    def render(self, *args, **kwargs) -> None:
        if self.current_scene:
            self.current_scene.render(*args, **kwargs)
