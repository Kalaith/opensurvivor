import arcade
import math

from ...core.entity import Entity
from ...content.items.experience import ExperienceOrb

class Enemy(Entity):
    def __init__(self, x: float, y: float, width: int = 24, height: int = 24, color=(255, 50, 50)):
        # Red square for enemy
        super().__init__(x, y, width, height, color)
        self.speed = 100.0
        self.target = None
        self.health = 1
        self.damage = 10

    def take_damage(self, amount: int, engine) -> bool:
        """Apply damage and return True if the enemy died."""
        self.health -= amount
        if self.health <= 0:
            self.on_death(engine)
            return True
        return False

    def on_death(self, engine):
        """Hook for subclasses to spawn new enemies or effects on death."""
        return None

    def update_target(self, dt: float):
        if self.target:
            # Simple tracking
            dx = self.target.center_x - self.center_x
            dy = self.target.center_y - self.center_y

            dist = math.sqrt(dx*dx + dy*dy)

            if dist > 0:
                dx /= dist
                dy /= dist

            # Set velocity with delta_time for smooth movement
            self.change_x = dx * self.speed * dt
            self.change_y = dy * self.speed * dt


class ArmoredEnemy(Enemy):
    """A sturdier enemy that takes multiple hits."""

    def __init__(self, x: float, y: float):
        super().__init__(x, y, 28, 28, (50, 100, 255))
        self.health = 3
        self.speed = 80.0


class SplittingEnemy(Enemy):
    """Enemy that splits into smaller versions on death."""

    def __init__(self, x: float, y: float, generation: int = 0):
        self.generation = generation
        size = 26 if generation == 0 else 18
        color = (120, 255, 120) if generation == 0 else (80, 200, 80)
        super().__init__(x, y, size, size, color)
        self.health = 1
        self.speed = 110.0 if generation == 0 else 140.0

    def on_death(self, engine):
        # Only split once
        if self.generation >= 1:
            return

        offsets = [(-12, 0), (12, 0)]
        for dx, dy in offsets:
            child = SplittingEnemy(self.center_x + dx, self.center_y + dy, generation=self.generation + 1)
            child.target = self.target
            engine.enemies.append(child)
            engine.all_sprites.append(child)


class ExploderEnemy(Enemy):
    """A circular enemy that explodes on death, damaging nearby units."""

    def __init__(self, x: float, y: float):
        diameter = 24
        super().__init__(x, y, diameter, diameter, (255, 180, 50))
        # Swap the solid color square for a circle texture
        self.texture = arcade.make_circle_texture(diameter, self.color)
        self.speed = 95.0
        self.health = 2
        self.explosion_radius = 80
        self.explosion_damage = 1

    def on_death(self, engine):
        player = engine.player
        defeated_enemies = []

        # Damage nearby enemies (excluding self)
        for other in list(engine.enemies):
            if other is self:
                continue

            if self._is_within_explosion(other):
                died = other.take_damage(self.explosion_damage, engine)
                if died:
                    defeated_enemies.append(other)

        # Award XP and remove defeated enemies immediately so they don't linger
        for enemy in defeated_enemies:
            orb = ExperienceOrb(enemy.center_x, enemy.center_y)
            engine.items.append(orb)
            engine.all_sprites.append(orb)
            enemy.remove_from_sprite_lists()

        # Damage the player if they're inside the blast
        if player and self._is_within_explosion(player):
            player.take_damage(self.explosion_damage)
            engine.sound_manager.play("hit")
            if player.health <= 0:
                engine.close()

    def _is_within_explosion(self, sprite) -> bool:
        dx = sprite.center_x - self.center_x
        dy = sprite.center_y - self.center_y
        return dx * dx + dy * dy <= self.explosion_radius * self.explosion_radius
