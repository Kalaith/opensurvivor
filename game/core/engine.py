import arcade
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

        self.elapsed_time = 0.0
        
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

        self._draw_hud()

        # Draw level-up overlay
        self.leveling_system.draw()

    def on_update(self, delta_time: float):
        """Update game state."""
        if self.paused:
            return

        self.elapsed_time += delta_time

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

    def _draw_hud(self):
        padding = 20
        bar_width = 260
        bar_height = 18
        time_text = arcade.Text(
            f"Survival: {self._format_elapsed_time()}",
            padding,
            padding,
            arcade.color.WHITE,
            16,
        )

        if self.player and self.player.health > 0:
            hp_ratio = (
                self.player.health / self.player.max_health if self.player.max_health else 0
            )
            xp_ratio = (
                self.player.xp / self.player.xp_to_next_level
                if self.player.xp_to_next_level
                else 0
            )

            hp_y = self.height - padding - bar_height / 2
            xp_y = hp_y - bar_height - 8

            self._draw_bar(
                padding + bar_width / 2,
                hp_y,
                bar_width,
                bar_height,
                hp_ratio,
                (200, 0, 0),
                (60, 20, 20),
                f"HP {self.player.health:.0f}/{self.player.max_health}",
            )

            self._draw_bar(
                padding + bar_width / 2,
                xp_y,
                bar_width,
                bar_height,
                xp_ratio,
                (20, 120, 220),
                (20, 40, 80),
                f"XP {self.player.xp:.0f}/{self.player.xp_to_next_level}",
            )

            time_text.draw()
        else:
            game_over = arcade.Text(
                "Game Over",
                self.width / 2,
                self.height - padding - 30,
                arcade.color.WHITE,
                28,
                anchor_x="center",
            )
            game_over.draw()

            time_text.center_x = self.width / 2
            time_text.center_y = self.height - padding - 70
            time_text.anchor_x = "center"
            time_text.draw()

    def _draw_bar(self, x, y, width, height, ratio, fill_color, background_color, label):
        clamped_ratio = max(0.0, min(1.0, ratio))
        arcade.draw_rectangle_filled(x, y, width, height, background_color)

        filled_width = width * clamped_ratio
        left = x - width / 2
        if filled_width > 0:
            arcade.draw_rectangle_filled(
                left + filled_width / 2, y, filled_width, height, fill_color
            )

        text = arcade.Text(label, left + 6, y - height / 2 + 2, arcade.color.WHITE, 12)
        text.draw()

    def _format_elapsed_time(self) -> str:
        minutes = int(self.elapsed_time) // 60
        seconds = int(self.elapsed_time) % 60
        return f"{minutes:02d}:{seconds:02d}"
