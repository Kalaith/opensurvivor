import os
import sys
import types

# Ensure the repository root is importable so game modules can be loaded in tests.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

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
arcade_stub.key = types.SimpleNamespace(
    W=1,
    A=2,
    S=3,
    D=4,
    UP=5,
    DOWN=6,
    LEFT=7,
    RIGHT=8,
    F10=9,
    KEY_1=10,
    KEY_2=11,
    KEY_3=12,
    MOD_CTRL=1 << 8,
    MOD_SHIFT=1 << 9,
)

sys.modules["arcade"] = arcade_stub

# Ensure arcade/pyglet run in headless mode during any accidental fallbacks.
os.environ.setdefault("PYGLET_HEADLESS", "true")
