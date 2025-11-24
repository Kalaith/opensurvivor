import arcade
from typing import Iterable, Tuple


class MapDefinition:
    """Basic rectangular map with optional static obstacles."""

    def __init__(
        self,
        width: int = 1280,
        height: int = 720,
        obstacle_data: Iterable[Tuple[float, float, int, int]] | None = None,
        background_color: tuple[int, int, int] = (25, 25, 40),
        grid_color: tuple[int, int, int] = (40, 40, 60),
        grid_spacing: int = 128,
    ) -> None:
        self.width = width
        self.height = height
        self.background_color = background_color
        self.grid_color = grid_color
        self.grid_spacing = grid_spacing
        self.obstacles = arcade.SpriteList(use_spatial_hash=True)

        if obstacle_data is None:
            obstacle_data = [
                (width * 0.5, height * 0.5, 80, 80),
                (width * 0.3, height * 0.6, 40, 140),
                (width * 0.7, height * 0.35, 120, 40),
            ]

        self._build_obstacles(obstacle_data)

    def _build_obstacles(self, obstacle_data: Iterable[Tuple[float, float, int, int]]) -> None:
        for center_x, center_y, width, height in obstacle_data:
            block = arcade.SpriteSolidColor(width, height, (70, 70, 90))
            block.center_x = center_x
            block.center_y = center_y
            self.obstacles.append(block)
