import os
import sys
import types

# Provide a lightweight stub of the arcade module so tests can run without
# graphical dependencies. Pytest loads this conftest before importing the
# application modules, ensuring the stub is in place when they are imported.
arcade_stub = types.ModuleType("arcade")


class _Window:
    def __init__(self, width=0, height=0, title=""):
        self.width = width
        self.height = height


class _SpriteList(list):
    def __init__(self, *args, **kwargs):
        super().__init__()

    def draw(self):
        return None

    def update(self):
        return None


class _Sprite:
    def __init__(self, width=0, height=0):
        self.width = width
        self.height = height
        self.center_x = 0
        self.center_y = 0
        self.change_x = 0
        self.change_y = 0


class _SpriteSolidColor:
    def __init__(self, width, height, color):
        self.width = width
        self.height = height
        self.color = color
        self.center_x = 0
        self.center_y = 0


class _Text:
    def __init__(self, *args, **kwargs):
        pass

    def draw(self):
        return None


def _noop(*_args, **_kwargs):
    return None


def _check_for_collision_with_list(*_args, **_kwargs):
    return []


arcade_stub.Window = _Window
arcade_stub.SpriteList = _SpriteList
arcade_stub.Sprite = _Sprite
arcade_stub.SpriteSolidColor = _SpriteSolidColor
arcade_stub.Text = _Text
arcade_stub.check_for_collision_with_list = _check_for_collision_with_list
arcade_stub.set_background_color = _noop
arcade_stub.draw_lrtb_rectangle_filled = _noop
arcade_stub.draw_line = _noop
arcade_stub.run = _noop
arcade_stub.color = types.SimpleNamespace(YELLOW=(255, 255, 0), WHITE=(255, 255, 255))

sys.modules["arcade"] = arcade_stub

# Ensure arcade/pyglet run in headless mode during any accidental fallbacks.
os.environ.setdefault("PYGLET_HEADLESS", "true")
