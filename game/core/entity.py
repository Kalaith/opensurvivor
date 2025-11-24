import arcade
from typing import Tuple

class Entity(arcade.SpriteSolidColor):
    """
    Base entity class inheriting from arcade.SpriteSolidColor.
    """
    def __init__(self, x: float, y: float, width: int, height: int, color: Tuple[int, int, int]):
        super().__init__(width, height, color)
        self.center_x = x
        self.center_y = y
        
        # Velocity is handled by arcade's change_x and change_y
        # We can keep a speed attribute for logic
        self.speed = 0.0

    def update(self, delta_time: float = 1/60):
        """Update entity state."""
        # arcade.Sprite.update() automatically adds change_x to center_x and change_y to center_y
        super().update()
        
        # If we need custom position logic (like floats vs ints), arcade handles floats fine.
