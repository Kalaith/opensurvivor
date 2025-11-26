import arcade
import types

import pytest

from game.content.characters.enemy import Enemy
from game.content.map import MapDefinition
from game.systems.combat import CombatSystem
from game.systems.collision import CollisionSystem
from game.systems.spawning import SpawningSystem


class DummyPlayer:
    def __init__(self, x, y):
        self.center_x = x
        self.center_y = y
        self.health = 1
        self.width = 24
        self.height = 24
        self.projectile_size = 1
        self.projectile_speed = 1
        self.projectile_lifetime = 1
        self.projectile_pierce = 1
        self.attack_speed_multiplier = 1.0

    def has_weapon(self, _name: str) -> bool:
        return False

    def take_damage(self, _amount):
        return None


class CountingEnemy(Enemy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_updates = 0

    def update_target(self, dt: float):
        self.target_updates += 1
        super().update_target(dt)


class DummyEngine:
    def __init__(self):
        self.map = MapDefinition(width=400, height=400, obstacle_data=[])
        self.elapsed_time = 0.0
        self.player = DummyPlayer(350, 350)
        self.enemies = arcade.SpriteList()
        self.projectiles = arcade.SpriteList()
        self.items = arcade.SpriteList()
        self.all_sprites = arcade.SpriteList()
        self.obstacles = self.map.obstacles
        self.sound_manager = types.SimpleNamespace(play=lambda *_, **__: None)

        self.spawning_system = SpawningSystem(self)
        self.combat_system = CombatSystem(self)
        self.collision_system = CollisionSystem()


@pytest.fixture
def engine():
    return DummyEngine()


def test_enemy_reacquires_after_player_returns(engine):
    enemy = CountingEnemy(40, 40)
    enemy.target = engine.player
    engine.enemies.append(enemy)

    # Run enough frames to move the enemy into a throttled state while the
    # player stays outside the engagement radius.
    for _ in range(10):
        engine.combat_system.update(0.1)
    throttled_calls = enemy.target_updates
    assert throttled_calls < 10

    # Move the player closer and ensure the enemy immediately refreshes.
    engine.player.center_x = 80
    engine.player.center_y = 80
    engine.combat_system.update(0.1)
    assert enemy.target_updates > throttled_calls


def test_collision_separation_moves_idle_enemies(engine):
    enemy_a = Enemy(100, 100)
    enemy_b = Enemy(100, 100)
    enemy_a.target = engine.player
    enemy_b.target = engine.player
    # Pretend the enemies have been idle long enough to be throttled.
    enemy_a.idle_frames = 20
    enemy_b.idle_frames = 20
    enemy_a.target_cooldown = 1.0
    enemy_b.target_cooldown = 1.0

    engine.enemies.extend([enemy_a, enemy_b])
    engine.all_sprites.extend(engine.enemies)

    engine.collision_system.update(engine, 0.016)

    assert (enemy_a.center_x, enemy_a.center_y) != (enemy_b.center_x, enemy_b.center_y)
