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

        # Health
        self.max_health = 100
        self.health = self.max_health
        self.regen_rate = 5  # Health per second
        self.regen_cooldown = 2.0  # Delay after taking damage before regen resumes
        self._regen_timer = 0.0

    def take_damage(self, amount: int):
        """Reduce health and reset regen timer."""
        self.health = max(0, self.health - amount)
        self._regen_timer = self.regen_cooldown

    def regenerate(self, dt: float):
        """Regenerate health over time after the cooldown."""
        if self.health <= 0:
            return

        if self._regen_timer > 0:
            self._regen_timer = max(0.0, self._regen_timer - dt)
            return

        if self.health < self.max_health:
            self.health = min(self.max_health, self.health + self.regen_rate * dt)
