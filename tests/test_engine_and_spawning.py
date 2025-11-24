import types
import random

import arcade

from game.core.engine import Engine
from game.systems.spawning import SpawningSystem


def _build_engine_stub():
    engine = Engine.__new__(Engine)
    engine.map = types.SimpleNamespace(width=100, height=80)
    return engine


def test_clamp_to_map_limits_sprite_to_bounds():
    engine = _build_engine_stub()
    sprite = types.SimpleNamespace(
        width=20,
        height=10,
        center_x=150.0,
        center_y=-5.0,
        change_x=5.0,
        change_y=-3.0,
    )

    engine._clamp_to_map(sprite)

    assert sprite.center_x == engine.map.width - sprite.width / 2
    assert sprite.center_y == sprite.height / 2
    assert sprite.change_x == 0
    assert sprite.change_y == 0


def test_apply_bounds_resets_position_on_collision(monkeypatch):
    engine = _build_engine_stub()
    engine.obstacles = object()

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
    engine._clamp_to_map = lambda _sprite: None

    engine._apply_bounds_and_collisions(sprite, (10.0, 10.0))

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
