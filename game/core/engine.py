from pathlib import Path

import arcade

from .audio import SoundManager
from .input import InputHandler
from ..content.characters.player import Player
from ..content.map import MapDefinition
from ..scenes import GameOverScene, GameplayScene, MenuScene
from ..scenes.base import BaseScene
from ..systems.combat import CombatSystem
from ..systems.leveling import LevelingSystem
from ..systems.spawning import SpawningSystem

class Engine(arcade.Window):
    """
    Core game engine that handles the main loop, event processing, and rendering.
    """
    def __init__(
        self,
        width: int = 1280,
        height: int = 720,
        title: str = "Open Survivor",
        map_definition: MapDefinition | None = None,
    ):
        # Build or accept the map definition before creating the window so the
        # window dimensions stay aligned with the intended playfield.
        self.map = map_definition or MapDefinition(width=width, height=height)

        super().__init__(int(self.map.width), int(self.map.height), title)

        self.input_handler = InputHandler()

        # Audio
        sfx_path = Path(__file__).resolve().parent.parent / "content" / "sfx"
        self.sound_manager = SoundManager(
            sfx_path,
            volume_config={
                "master": 0.6,
                "sfx": {
                    "attack": 0.35,
                    "hit": 0.4,
                    "xp_collect": 0.3,
                    "level_up": 0.6,
                },
            },
        )
        self.sound_manager.load_sounds()
        # Map definition and obstacles

        # Sprite lists
        self.all_sprites = arcade.SpriteList()
        self.enemies = arcade.SpriteList()
        self.projectiles = arcade.SpriteList()
        self.items = arcade.SpriteList()
        self.obstacles = self.map.obstacles
        self.player = None
        self.paused = False
        self.elapsed_time = 0.0

        # Game flow and progression
        self.selected_character = "square"
        self.current_character = None
        self.last_score = 0.0
        self.best_survival_times: dict[str, float] = {
            "square": 0.0,
            "triangle": 0.0,
            "circle": 0.0,
        }
        self.unlocked_characters: set[str] = {"square"}

        # UI regions
        self.card_regions: dict[str, dict[str, float]] = {}
        self.start_button = {"x": self.width / 2, "y": 120, "w": 220, "h": 50}
        self.menu_background_color = (25, 25, 35)
        self.return_button = {"x": self.width / 2, "y": 120, "w": 240, "h": 50}

        self._setup_characters()
        
        # Systems
        self.spawning_system = SpawningSystem(self)
        self.combat_system = CombatSystem(self)
        self.leveling_system = LevelingSystem(self)

        # Set background color
        arcade.set_background_color((30, 30, 30))

        # Scenes
        self.current_scene: BaseScene | None = None
        self.menu_scene = MenuScene(self)
        self.game_over_scene = GameOverScene(self)

        self.change_scene(self.menu_scene)

    def _setup_characters(self) -> None:
        self.characters = {
            "square": {
                "name": "Square",
                "color": (0, 128, 255),
                "starting_weapons": {"projectile"},
                "blurb": "Straight shooter with a focused projectile.",
                "unlock": None,
            },
            "triangle": {
                "name": "Triangle",
                "color": (255, 120, 0),
                "starting_weapons": {"orbitals"},
                "blurb": "Spins blades around itself to clear space.",
                "unlock": {"character": "square", "seconds": 600},
            },
            "circle": {
                "name": "Circle",
                "color": (120, 220, 120),
                "starting_weapons": {"cardinal"},
                "blurb": "Fires a spread of projectiles in all directions.",
                "unlock": {"character": "triangle", "seconds": 600},
            },
        }

        margin = 30
        card_width = 280
        card_height = 160
        start_x = (self.width - (card_width * 3 + margin * 2)) / 2 + card_width / 2
        center_y = self.height / 2 + 80
        for idx, key in enumerate(["square", "triangle", "circle"]):
            center_x = start_x + idx * (card_width + margin)
            self.card_regions[key] = {"x": center_x, "y": center_y, "w": card_width, "h": card_height}

    def change_scene(self, scene: BaseScene) -> None:
        if self.current_scene is scene:
            return

        if self.current_scene:
            self.current_scene.on_exit()

        self.current_scene = scene
        self.current_scene.on_enter()

    def return_to_menu(self) -> None:
        self.change_scene(self.menu_scene)

    def set_player(self, player):
        self.player = player
        self.all_sprites.append(player)

    def start_game(self, character_key: str):
        if character_key not in self.unlocked_characters:
            return

        self._reset_run_state()
        definition = self.characters[character_key]
        start_x = self.map.width / 2
        start_y = self.map.height / 2
        player = Player(
            start_x,
            start_y,
            color=definition["color"],
            starting_weapons=definition["starting_weapons"],
        )
        self.set_player(player)
        self.current_character = character_key
        gameplay_scene = GameplayScene(self)
        self.change_scene(gameplay_scene)

    def _reset_run_state(self):
        self.all_sprites = arcade.SpriteList()
        self.enemies = arcade.SpriteList()
        self.projectiles = arcade.SpriteList()
        self.items = arcade.SpriteList()
        self.elapsed_time = 0.0
        self.paused = False
        self.spawning_system = SpawningSystem(self)
        self.combat_system = CombatSystem(self)
        self.leveling_system = LevelingSystem(self)

    def start(self):
        """Start the game loop."""
        arcade.run()

    def on_draw(self):
        """Render the active scene."""
        self.clear()

        if self.current_scene:
            self.current_scene.render()

    def on_update(self, delta_time: float):
        """Update the active scene."""
        if self.current_scene:
            self.current_scene.update(delta_time)

    def on_key_press(self, key, modifiers):
        if self.current_scene:
            self.current_scene.handle_key_press(key, modifiers)

    def on_key_release(self, key, modifiers):
        if self.current_scene:
            self.current_scene.handle_key_release(key, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        if self.current_scene:
            self.current_scene.handle_mouse_motion(x, y, dx, dy)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.current_scene:
            self.current_scene.handle_mouse_press(x, y, button, modifiers)

    def draw_bar(self, x, y, width, height, ratio, fill_color, background_color, label):
        clamped_ratio = max(0.0, min(1.0, ratio))
        # x, y are center coordinates. Convert to bottom-left for lbwh.
        arcade.draw_lbwh_rectangle_filled(x - width / 2, y - height / 2, width, height, background_color)

        filled_width = width * clamped_ratio
        left = x - width / 2
        if filled_width > 0:
            arcade.draw_lbwh_rectangle_filled(
                left, y - height / 2, filled_width, height, fill_color
            )

        text = arcade.Text(label, left + 6, y - height / 2 + 2, arcade.color.WHITE, 12)
        text.draw()

    def format_elapsed_time(self) -> str:
        minutes = int(self.elapsed_time) // 60
        seconds = int(self.elapsed_time) % 60
        return f"{minutes:02d}:{seconds:02d}"

    def format_time_value(self, seconds_value: float) -> str:
        minutes = int(seconds_value) // 60
        seconds = int(seconds_value) % 60
        return f"{minutes:02d}:{seconds:02d}"

    def weapon_label(self, weapon_key: str) -> str:
        names = {
            "projectile": "Straight Shot",
            "orbitals": "Spinning Blades",
            "cardinal": "Spread Burst",
        }
        return names.get(weapon_key, weapon_key)

    def record_survival_time(self):
        if not self.current_character:
            return
        best = self.best_survival_times.get(self.current_character, 0.0)
        self.best_survival_times[self.current_character] = max(best, self.last_score)

    def update_unlocks(self):
        if self.current_character:
            best = self.best_survival_times.get(self.current_character, 0.0)
            if self.elapsed_time > best:
                self.best_survival_times[self.current_character] = self.elapsed_time

        if self.best_survival_times.get("square", 0.0) >= 600:
            self.unlocked_characters.add("triangle")
        if self.best_survival_times.get("triangle", 0.0) >= 600:
            self.unlocked_characters.add("circle")

    def handle_game_over(self):
        self.last_score = self.elapsed_time
        self.record_survival_time()
        self.update_unlocks()

        self.change_scene(self.game_over_scene)

        # Clear active sprites so the next run starts fresh
        self.all_sprites = arcade.SpriteList()
        self.enemies = arcade.SpriteList()
        self.projectiles = arcade.SpriteList()
        self.items = arcade.SpriteList()
        self.player = None
