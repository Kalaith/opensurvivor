import arcade
from .input import InputHandler
from ..content.map import MapDefinition
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

        # Map definition and obstacles
        self.map = MapDefinition(width=width, height=height)

        # Sprite lists
        self.all_sprites = arcade.SpriteList()
        self.enemies = arcade.SpriteList()
        self.projectiles = arcade.SpriteList()
        self.items = arcade.SpriteList()
        self.obstacles = self.map.obstacles
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

        # Draw map background
        arcade.draw_lrtb_rectangle_filled(
            0,
            self.map.width,
            self.map.height,
            0,
            color=(25, 25, 40),
        )

        # Draw a subtle grid for spatial reference
        grid_spacing = 128
        grid_color = (40, 40, 60)
        for x in range(0, int(self.map.width) + 1, grid_spacing):
            arcade.draw_line(x, 0, x, self.map.height, grid_color, 1)
        for y in range(0, int(self.map.height) + 1, grid_spacing):
            arcade.draw_line(0, y, self.map.width, y, grid_color, 1)

        # Draw obstacles
        self.obstacles.draw()
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
        movers = []
        if self.player:
            movers.append(self.player)
        movers.extend(self.enemies)
        previous_positions = {sprite: (sprite.center_x, sprite.center_y) for sprite in movers}

        self.all_sprites.update()

        for sprite in movers:
            self._apply_bounds_and_collisions(sprite, previous_positions.get(sprite))

    def on_key_press(self, key, modifiers):
        if self.leveling_system.handle_input(key):
            return
        self.input_handler.on_key_press(key, modifiers)

    def on_key_release(self, key, modifiers):
        self.input_handler.on_key_release(key, modifiers)

    def _apply_bounds_and_collisions(self, sprite: arcade.Sprite, previous_pos):
        """Clamp sprites to the map bounds and prevent passing through obstacles."""
        if previous_pos is None:
            return

        collided = False
        if self.obstacles:
            collided = bool(arcade.check_for_collision_with_list(sprite, self.obstacles))
        if collided:
            sprite.center_x, sprite.center_y = previous_pos
            sprite.change_x = 0
            sprite.change_y = 0

        half_w = sprite.width / 2
        half_h = sprite.height / 2
        clamped_x = min(max(sprite.center_x, half_w), self.map.width - half_w)
        clamped_y = min(max(sprite.center_y, half_h), self.map.height - half_h)

        if clamped_x != sprite.center_x or clamped_y != sprite.center_y:
            sprite.center_x = clamped_x
            sprite.center_y = clamped_y
            sprite.change_x = 0
            sprite.change_y = 0
