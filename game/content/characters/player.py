from ...core.entity import Entity
from typing import Tuple

class Player(Entity):
    def __init__(self, x: float, y: float, color: Tuple[int, int, int] | None = None, starting_weapons: set[str] | None = None):
        # Character appearance can be customized via color
        player_color = color or (0, 128, 255)
        super().__init__(x, y, 32, 32, player_color)
        self.speed = 200.0  # Pixels per second

        # Stats
        self.xp = 0
        self.level = 1
        self.xp_to_next_level = 100

        # Weapon stats
        self.projectile_size = 8
        self.projectile_speed = 400.0
        self.projectile_lifetime = 2.0
        self.projectile_pierce = 1
        self.attack_speed_multiplier = 1.0

        # Survivability
        self.invincible = False
        
        # Health
        self.max_health = 100
        self.health = self.max_health
        self.regen_rate = 5  # Health per second
        self.regen_cooldown = 2.0  # Delay after taking damage before regen resumes
        self._regen_timer = 0.0

        # Weapons
        self.unlocked_weapons = set(starting_weapons) if starting_weapons else {"projectile"}

    def unlock_weapon(self, weapon_name: str):
        self.unlocked_weapons.add(weapon_name)

    def has_weapon(self, weapon_name: str) -> bool:
        return weapon_name in self.unlocked_weapons

    def take_damage(self, amount: int):
        """Reduce health and reset regen timer."""
        if self.invincible:
            return
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
