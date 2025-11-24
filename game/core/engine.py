from pathlib import Path
import arcade
from .audio import SoundManager
from .input import InputHandler
from ..systems.spawning import SpawningSystem
from ..systems.combat import CombatSystem
from ..systems.leveling import LevelingSystem

class Engine(arcade.Window):
    """
    Core game engine that handles the main loop, event processing, and rendering.
    """
    def __init__(self, width: int = 1280, height: int = 720, title: str = "Open Survivor"):
        super().__init__(width, height, title)
        
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

        # Sprite lists
        self.all_sprites = arcade.SpriteList()
        self.enemies = arcade.SpriteList()
        self.projectiles = arcade.SpriteList()
        self.items = arcade.SpriteList()
        self.player = None
        self.paused = False
        
        # Systems
        self.spawning_system = SpawningSystem(self)
        self.combat_system = CombatSystem(self)
        self.leveling_system = LevelingSystem(self)
        
        # Set background color
        arcade.set_background_color((30, 30, 30))

    def set_player(self, player):
        self.player = player
        self.all_sprites.append(player)

    def start(self):
        """Start the game loop."""
        arcade.run()

    def on_draw(self):
        """Render the game."""
        self.clear()
        self.all_sprites.draw()

        # Draw UI / Debug info
        if self.player:
            health_text = f"HP: {self.player.health:.0f}/{self.player.max_health}"
            info_text = (
                f"Pos: ({self.player.center_x:.1f}, {self.player.center_y:.1f}) | "
                f"Enemies: {len(self.enemies)} | {health_text} | "
                f"Level: {self.player.level} | XP: {self.player.xp}/{self.player.xp_to_next_level}"
            )
            text = arcade.Text(info_text, 10, 10, arcade.color.WHITE, 14)
            text.draw()

        # Draw level-up overlay
        self.leveling_system.draw()

    def on_update(self, delta_time: float):
        """Update game state."""
        if self.paused:
            return

        # Handle Player Movement
        if self.player:
            mx, my = self.input_handler.get_movement_vector()
            self.player.change_x = mx * self.player.speed * delta_time
            self.player.change_y = my * self.player.speed * delta_time
            self.player.regenerate(delta_time)

        # Update Systems
        self.spawning_system.update(delta_time)
        self.combat_system.update(delta_time)
        self.leveling_system.update(delta_time)

        # Update all sprites (this applies change_x/change_y to positions)
        self.all_sprites.update()

    def on_key_press(self, key, modifiers):
        if self.leveling_system.handle_input(key):
            return
        self.input_handler.on_key_press(key, modifiers)

    def on_key_release(self, key, modifiers):
        self.input_handler.on_key_release(key, modifiers)
