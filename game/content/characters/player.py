from ...core.entity import Entity
from typing import Tuple

class Player(Entity):
    def __init__(self, x: float, y: float):
        # Blue square for player
        super().__init__(x, y, 32, 32, (0, 128, 255))
        self.speed = 200.0  # Pixels per second
        
        # Stats
        self.xp = 0
        self.level = 1
        self.xp_to_next_level = 100
