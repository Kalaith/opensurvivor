import random
import types

import arcade

from game.core.engine import Engine
from game.systems.collision import CollisionSystem
from game.systems.spawning import SpawningSystem
from game.systems.progression import ProgressionState, ProgressionSystem
from game.content.characters.enemy import ExploderEnemy


def _build_engine_stub():
    map_stub = types.SimpleNamespace(width=100, height=80)
    return map_stub


def test_clamp_to_map_limits_sprite_to_bounds():
    map_stub = _build_engine_stub()
    collision_system = CollisionSystem()
    sprite = types.SimpleNamespace(
        width=20,
        height=10,
        center_x=150.0,
        center_y=-5.0,
        change_x=5.0,
        change_y=-3.0,
    )

    collision_system.clamp_to_map(sprite, map_stub)

    assert sprite.center_x == map_stub.width - sprite.width / 2
    assert sprite.center_y == sprite.height / 2
    assert sprite.change_x == 0
    assert sprite.change_y == 0


def test_apply_bounds_resets_position_on_collision(monkeypatch):
    map_stub = _build_engine_stub()
    collision_system = CollisionSystem()
    obstacles = object()

    sprite = types.SimpleNamespace(
        center_x=20.0,
        center_y=20.0,
        change_x=5.0,
        change_y=5.0,
        width=10,
        height=10,
    )

    monkeypatch.setattr(
        arcade,
        "check_for_collision_with_list",
        lambda *_args, **_kwargs: [True],
    )
    collision_system.clamp_to_map = lambda _sprite, _map: None

    collision_system.apply_bounds_and_collisions(
        sprite, (10.0, 10.0), obstacles=obstacles, game_map=map_stub
    )

    assert (sprite.center_x, sprite.center_y) == (10.0, 10.0)
    assert sprite.change_x == 0
    assert sprite.change_y == 0


class DummyEnemy:
    def __init__(self, x, y):
        self.center_x = x
        self.center_y = y
        self.health = 10
        self.speed = 1.0
        self.color = (100, 100, 100)
        self.is_elite = False


class DummyMap:
    def __init__(self):
        self.width = 50
        self.height = 60


def test_spawn_enemy_respects_wave_weights(monkeypatch):
    engine = types.SimpleNamespace(
        map=DummyMap(),
        enemies=[],
        all_sprites=[],
        player=None,
        elapsed_time=0.0,
    )
    system = SpawningSystem(engine)

    chosen_types = []

    def _fake_select():
        choice = DummyEnemy if len(chosen_types) % 2 == 0 else DummyEnemy
        chosen_types.append(choice)
        return choice

    monkeypatch.setattr(system, "_select_enemy_class", _fake_select)
    monkeypatch.setattr(random, "choice", lambda _seq: "top")
    monkeypatch.setattr(random, "uniform", lambda a, b: (a + b) / 2)
    monkeypatch.setattr(random, "random", lambda: 1.0)

    system.spawn_enemy()

    assert len(engine.enemies) == 1
    assert isinstance(engine.enemies[0], DummyEnemy)
    assert engine.enemies[0].center_y == engine.map.height + 50
    assert len(chosen_types) == 1


def test_exploder_enemy_triggers_game_over_and_cleanup():
    # Construct a minimal engine with the necessary state but without running Engine.__init__.
    engine = Engine.__new__(Engine)
    engine.state = "playing"
    engine.progression_state = ProgressionState(
        elapsed_time=12.5,
        current_character="square",
        best_survival_times={"square": 5.0, "triangle": 0.0, "circle": 0.0},
        unlocked_characters=set(),
    )
    engine.progression_system = ProgressionSystem(
        {
            "square": {"unlock": None},
            "triangle": {"unlock": {"character": "square", "seconds": 600}},
            "circle": {"unlock": {"character": "triangle", "seconds": 600}},
        }
    )
    engine.all_sprites = [1]
    engine.enemies = []
    engine.projectiles = [1]
    engine.items = [1]
    engine.sound_manager = types.SimpleNamespace(play=lambda *_args, **_kwargs: None)

    class DummyPlayer:
        def __init__(self):
            self.center_x = 0
            self.center_y = 0
            self.health = 1
            self.max_health = 1

        def take_damage(self, amount):
            self.health = max(0, self.health - amount)

    player = DummyPlayer()
    engine.player = player

    # Bind the real handle_game_over method to the stub engine instance.
    engine.handle_game_over = types.MethodType(Engine.handle_game_over, engine)

    enemy = ExploderEnemy.__new__(ExploderEnemy)
    enemy.center_x = 0
    enemy.center_y = 0
    enemy.explosion_radius = 10
    enemy.explosion_damage = 1

    enemy.on_death(engine)

    assert engine.state == "game_over"
    assert engine.progression_state.last_score == engine.progression_state.elapsed_time
    assert (
        engine.progression_state.best_survival_times["square"]
        == engine.progression_state.elapsed_time
    )
    assert engine.player is None
    assert len(engine.all_sprites) == 0
    assert len(engine.projectiles) == 0
    assert len(engine.items) == 0
