from __future__ import annotations

from pathlib import Path

import arcade

from .audio import SoundManager
from .input import InputHandler
from ..content.characters.player import Player
from ..content.map import MapDefinition
from ..scenes import BaseScene, GameOverScene, GameplayScene, MenuScene
from ..systems.collision import CollisionSystem
from ..systems.combat import CombatSystem
from ..systems.leveling import LevelingSystem
from ..systems.progression import ProgressionState, ProgressionSystem
from ..systems.spawning import SpawningSystem


class Engine(arcade.Window):
    """Core game engine that drives the scene lifecycle and shared systems."""

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

        self.all_sprites = arcade.SpriteList()
        self.enemies = arcade.SpriteList()
        self.projectiles = arcade.SpriteList()
        self.items = arcade.SpriteList()
        self.obstacles = self.map.obstacles
        self.player: Player | None = None
        self.paused = False
        self.state = "menu"

        self.progression_state = ProgressionState()

        self.characters: dict[str, dict[str, object]] = {}
        self.card_regions: dict[str, dict[str, float]] = {}
        self.start_button = {"x": self.width / 2, "y": 120, "w": 220, "h": 50}
        self.menu_background_color = (25, 25, 35)
        self.return_button = {"x": self.width / 2, "y": 120, "w": 240, "h": 50}
        self._setup_characters()

        self.progression_system = ProgressionSystem(self.characters)

        # Systems are created when a run begins so they always start fresh.
        self.spawning_system: SpawningSystem | None = None
        self.combat_system: CombatSystem | None = None
        self.leveling_system: LevelingSystem | None = None
        self.collision_system: CollisionSystem | None = None

        arcade.set_background_color((30, 30, 30))

        # Scenes
        self.current_scene: BaseScene | None = None
        self.menu_scene = MenuScene(self)
        self.gameplay_scene = GameplayScene(self)
        self.game_over_scene = GameOverScene(self)

        self.change_scene(self.menu_scene)

    # Progression convenience properties
    @property
    def best_survival_times(self) -> dict[str, float]:
        return self.progression_state.best_survival_times

    @property
    def unlocked_characters(self) -> set[str]:
        return self.progression_state.unlocked_characters

    @property
    def elapsed_time(self) -> float:
        return self.progression_state.elapsed_time

    @elapsed_time.setter
    def elapsed_time(self, value: float) -> None:
        self.progression_state.elapsed_time = value

    @property
    def current_character(self) -> str | None:
        return self.progression_state.current_character

    @current_character.setter
    def current_character(self, value: str | None) -> None:
        self.progression_state.current_character = value

    @property
    def last_score(self) -> float:
        return self.progression_state.last_score

    @last_score.setter
    def last_score(self, value: float) -> None:
        self.progression_state.last_score = value

    def change_scene(self, scene: BaseScene) -> None:
        if self.current_scene is scene:
            return

        if self.current_scene:
            self.current_scene.on_exit()

        self.current_scene = scene
        self.current_scene.on_enter()

    def return_to_menu(self) -> None:
        self.state = "menu"
        self.change_scene(self.menu_scene)

    def set_player(self, player: Player) -> None:
        self.player = player
        self.all_sprites.append(player)

    def start_game(self, character_key: str) -> None:
        if character_key not in self.unlocked_characters:
            return

        definition = self.characters[character_key]
        self._reset_run_state(character_key)

        start_x = self.map.width / 2
        start_y = self.map.height / 2
        player = Player(
            start_x,
            start_y,
            color=definition["color"],
            starting_weapons=definition["starting_weapons"],
        )
        self.set_player(player)
        self.state = "playing"
        self.change_scene(self.gameplay_scene)

    def _reset_run_state(self, character_key: str) -> None:
        self.all_sprites = arcade.SpriteList()
        self.enemies = arcade.SpriteList()
        self.projectiles = arcade.SpriteList()
        self.items = arcade.SpriteList()
        self.paused = False

        self.spawning_system = SpawningSystem(self)
        self.combat_system = CombatSystem(self)
        self.leveling_system = LevelingSystem(self)
        self.collision_system = CollisionSystem()

        self.progression_system.start_run(
            self.progression_state, character_key=character_key
        )

    def handle_game_over(self) -> None:
        if self.state != "playing":
            return

        self.progression_system.record_game_over(self.progression_state)
        self.state = "game_over"
        self.change_scene(self.game_over_scene)

        # Clear active sprites so the next run starts fresh
        self.all_sprites = arcade.SpriteList()
        self.enemies = arcade.SpriteList()
        self.projectiles = arcade.SpriteList()
        self.items = arcade.SpriteList()
        self.player = None

    def update_unlocks(self) -> None:
        # Keep the progression model in sync with the currently tracked timers.
        self.progression_state.elapsed_time = self.elapsed_time
        self.progression_system.record_personal_best(self.progression_state)
        self.progression_system.unlock_rewards(self.progression_state)

    def start(self) -> None:
        arcade.run()

    def on_draw(self) -> None:
        """Render the active scene."""
        self.clear()

        if self.current_scene:
            self.current_scene.render()

    def on_update(self, delta_time: float) -> None:
        """Advance the active scene."""
        if self.current_scene:
            self.current_scene.update(delta_time)

    def on_key_press(self, key, modifiers) -> None:
        if self.current_scene:
            self.current_scene.handle_key_press(key, modifiers)

    def on_key_release(self, key, modifiers) -> None:
        if self.current_scene:
            self.current_scene.handle_key_release(key, modifiers)

    def on_mouse_motion(self, x, y, dx, dy) -> None:
        if self.current_scene:
            self.current_scene.handle_mouse_motion(x, y, dx, dy)

    def on_mouse_press(self, x, y, button, modifiers) -> None:
        if self.current_scene:
            self.current_scene.handle_mouse_press(x, y, button, modifiers)

    def draw_bar(self, x, y, width, height, ratio, fill_color, background_color, label):
        clamped_ratio = max(0.0, min(1.0, ratio))
        # x, y are center coordinates. Convert to bottom-left for lbwh.
        arcade.draw_lbwh_rectangle_filled(
            x - width / 2, y - height / 2, width, height, background_color
        )

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
            self.card_regions[key] = {
                "x": center_x,
                "y": center_y,
                "w": card_width,
                "h": card_height,
            }

    def _draw_map_background(self) -> None:
        """Render the arena area with a solid fill and grid."""
        arcade.draw_lrbt_rectangle_filled(
            0,
            self.map.width,
            0,
            self.map.height,
            color=self.map.background_color,
        )

        grid_spacing = self.map.grid_spacing
        grid_color = self.map.grid_color
        for x in range(0, int(self.map.width) + 1, grid_spacing):
            arcade.draw_line(x, 0, x, self.map.height, grid_color, 1)
        for y in range(0, int(self.map.height) + 1, grid_spacing):
            arcade.draw_line(0, y, self.map.width, y, grid_color, 1)
