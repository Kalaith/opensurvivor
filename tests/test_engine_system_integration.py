from unittest import mock

from game.core.gameplay_scene import GameplayScene


def test_gameplay_scene_runs_collision_before_progression():
    order = []
    collision = mock.Mock()
    progression = mock.Mock()
    hud = mock.Mock()

    collision.update.side_effect = lambda dt: order.append("collision")
    progression.update.side_effect = lambda dt: order.append("progression")

    scene = GameplayScene(collision, hud, progression)

    scene.update(0.25)

    assert order == ["collision", "progression"]
    collision.update.assert_called_once_with(0.25)
    progression.update.assert_called_once_with(0.25)


def test_gameplay_scene_renders_hud_with_progression_status():
    collision = mock.Mock()
    progression = mock.Mock()
    hud = mock.Mock()

    progression.get_status.return_value = {"hp": 3, "level": 2}
    scene = GameplayScene(collision, hud, progression)

    scene.render(surface="surface")

    progression.get_status.assert_called_once_with()
    hud.render.assert_called_once_with("surface", {"hp": 3, "level": 2})


def test_gameplay_scene_forwards_input_to_progression():
    collision = mock.Mock()
    progression = mock.Mock()
    hud = mock.Mock()

    scene = GameplayScene(collision, hud, progression)

    scene.handle_input({"key": "space"})

    progression.handle_input.assert_called_once_with({"key": "space"})
