from unittest import mock

from game.core.scene_manager import SceneManager, Scene


def test_scene_switch_triggers_exit_and_enter():
    manager = SceneManager()
    first_scene = mock.create_autospec(Scene, instance=True)
    second_scene = mock.create_autospec(Scene, instance=True)

    manager.switch_to(first_scene)
    manager.switch_to(second_scene)

    first_scene.on_enter.assert_called_once_with()
    first_scene.on_exit.assert_called_once_with()
    second_scene.on_enter.assert_called_once_with()


def test_scene_manager_delegates_to_active_scene():
    manager = SceneManager()
    scene = mock.create_autospec(Scene, instance=True)

    manager.switch_to(scene)
    manager.handle_input("event")
    manager.update(0.5)
    manager.render("surface")

    scene.handle_input.assert_called_once_with("event")
    scene.update.assert_called_once_with(0.5)
    scene.render.assert_called_once_with("surface")


def test_scene_manager_ignores_calls_without_scene():
    manager = SceneManager()

    # These should not raise or attempt to call into a missing scene.
    manager.handle_input("event")
    manager.update(0.1)
    manager.render(None)
