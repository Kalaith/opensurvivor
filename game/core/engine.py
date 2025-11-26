from pathlib import Path
import arcade
# TODO(engine-extraction): Rendering and window lifecycle currently depend directly
# on the arcade.Window base class; refactors will need to abstract drawing away
# from this inheritance.
from .audio import SoundManager
from .input import InputHandler
from ..content.map import MapDefinition
from ..content.characters.player import Player
# TODO(engine-extraction): Systems retain tight coupling by accepting Engine
# instance; consider dependency boundaries when separating systems.
from ..systems.spawning import SpawningSystem
from ..systems.combat import CombatSystem
from ..systems.leveling import LevelingSystem

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
        # TODO(engine-extraction): State bucket (world/terrain). Map definition
        # and obstacle lists live on the engine and feed into rendering/collision.

        # TODO(engine-extraction): Sprite aggregates used across systems (rendering
        # + collisions); likely move into scene graph or entity store.
        self.all_sprites = arcade.SpriteList()
        self.enemies = arcade.SpriteList()
        self.projectiles = arcade.SpriteList()
        self.items = arcade.SpriteList()
        self.obstacles = self.map.obstacles
        self.player = None
        self.paused = False
        self.elapsed_time = 0.0

        # TODO(engine-extraction): State transitions bucket — menu/playing/game_over
        # modes drive update/draw/input pathways.
        self.state = "menu"
        self.selected_character = "square"
        self.current_character = None
        self.last_score = 0.0
        self.best_survival_times: dict[str, float] = {
            "square": 0.0,
            "triangle": 0.0,
            "circle": 0.0,
        }
        self.unlocked_characters: set[str] = {"square"}

        # TODO(engine-extraction): HUD/UI bucket — menu/game-over layouts share
        # positional dicts living on the engine rather than a UI scene object.
        self.card_regions: dict[str, dict[str, float]] = {}
        self.start_button = {"x": self.width / 2, "y": 120, "w": 220, "h": 50}
        self.menu_background_color = (25, 25, 35)
        self.return_button = {"x": self.width / 2, "y": 120, "w": 240, "h": 50}

        self._setup_characters()
        
        # TODO(engine-extraction): Subsystem collaborators depend on Engine to
        # query sprites, state, and input; consider inversion for testability.
        self.spawning_system = SpawningSystem(self)
        self.combat_system = CombatSystem(self)
        self.leveling_system = LevelingSystem(self)

        # Set background color
        arcade.set_background_color((30, 30, 30))

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
        self.state = "playing"

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
        """Render the game."""
        self.clear()

        if self.state == "playing":
            # TODO(engine-extraction): Rendering bucket — map background, obstacles,
            # sprite batch, HUD, and wave notifications belong in a render scene.
            self._draw_map_background()

            # Draw obstacles inside the map bounds
            self.obstacles.draw()
            self.all_sprites.draw()

            self._draw_hud()

            notice = self.spawning_system.get_wave_notification()
            if notice:
                banner = arcade.Text(
                    notice,
                    self.width / 2,
                    self.height - 40,
                    arcade.color.YELLOW,
                    18,
                    anchor_x="center",
                )
                banner.draw()

            # Draw level-up overlay
            self.leveling_system.draw()
        elif self.state == "menu":
            # TODO(engine-extraction): HUD/UI bucket — menu scene rendering.
            self._draw_menu()
        elif self.state == "game_over":
            # TODO(engine-extraction): HUD/UI bucket — game over scene rendering.
            self._draw_game_over()

    def on_update(self, delta_time: float):
        """Update game state."""
        if self.state != "playing":
            return

        if self.paused:
            return

        self.elapsed_time += delta_time

        self._update_unlocks()

        # TODO(engine-extraction): Input coupling — movement pulls directly from
        # InputHandler tied to arcade window events.
        # Handle Player Movement
        if self.player:
            mx, my = self.input_handler.get_movement_vector()
            self.player.change_x = mx * self.player.speed * delta_time
            self.player.change_y = my * self.player.speed * delta_time
            self.player.regenerate(delta_time)

        # TODO(engine-extraction): Systems bucket — spawning, combat, leveling run
        # per-frame and expect to mutate engine-managed sprite lists.
        # Update Systems
        self.spawning_system.update(delta_time)
        self.combat_system.update(delta_time)
        self.leveling_system.update(delta_time)

        # TODO(engine-extraction): Movement/collision bucket — SpriteList update
        # followed by bounds+obstacle collision.
        # Update all sprites (this applies change_x/change_y to positions)
        movers = []
        if self.player:
            movers.append(self.player)
        movers.extend(self.enemies)
        previous_positions = [
            (sprite.center_x, sprite.center_y) for sprite in movers
        ]

        self.all_sprites.update()

        for sprite, previous_pos in zip(movers, previous_positions):
            self._apply_bounds_and_collisions(sprite, previous_pos)

    def on_key_press(self, key, modifiers):
        if self.state != "playing":
            return
        if self.leveling_system.handle_input(key):
            return
        self.input_handler.on_key_press(key, modifiers)

    def on_key_release(self, key, modifiers):
        if self.state != "playing":
            return
        self.input_handler.on_key_release(key, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        if self.state != "playing":
            return
        self.leveling_system.handle_mouse_motion(x, y, dx, dy)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.state == "menu":
            self._handle_menu_click(x, y)
            return
        if self.state == "game_over":
            self._handle_game_over_click(x, y)
            return
        if self.leveling_system.handle_mouse_press(x, y, button, modifiers):
            return

    # TODO(engine-extraction): Collision handling bucket — bounds + obstacle
    # resolution live here, tied to Arcade collision helpers and sprite state.
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

        self._clamp_to_map(sprite)

    def _clamp_to_map(self, sprite: arcade.Sprite) -> None:
        """Keep a sprite inside the map rectangle."""
        half_w = sprite.width / 2
        half_h = sprite.height / 2
        clamped_x = min(max(sprite.center_x, half_w), self.map.width - half_w)
        clamped_y = min(max(sprite.center_y, half_h), self.map.height - half_h)

        if clamped_x != sprite.center_x or clamped_y != sprite.center_y:
            sprite.center_x = clamped_x
            sprite.center_y = clamped_y
            sprite.change_x = 0
            sprite.change_y = 0

    def _handle_menu_click(self, x: float, y: float) -> None:
        for key, rect in self.card_regions.items():
            if abs(x - rect["x"]) <= rect["w"] / 2 and abs(y - rect["y"]) <= rect["h"] / 2:
                self.selected_character = key
                break

        if not self._can_start_selected_character():
            return

        if (
            abs(x - self.start_button["x"]) <= self.start_button["w"] / 2
            and abs(y - self.start_button["y"]) <= self.start_button["h"] / 2
        ):
            self.start_game(self.selected_character)

    def _handle_game_over_click(self, x: float, y: float) -> None:
        if (
            abs(x - self.return_button["x"]) <= self.return_button["w"] / 2
            and abs(y - self.return_button["y"]) <= self.return_button["h"] / 2
        ):
            self.state = "menu"

    def _can_start_selected_character(self) -> bool:
        return self.selected_character in self.unlocked_characters

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

    def _draw_menu(self):
        arcade.draw_lrbt_rectangle_filled(0, self.width, 0, self.height, self.menu_background_color)

        title = arcade.Text(
            "Open Survivor",
            self.width / 2,
            self.height - 120,
            arcade.color.WHITE,
            36,
            anchor_x="center",
        )
        subtitle = arcade.Text(
            "Choose your character to begin",
            self.width / 2,
            self.height - 170,
            arcade.color.LIGHT_GRAY,
            18,
            anchor_x="center",
        )
        title.draw()
        subtitle.draw()

        for key in ["square", "triangle", "circle"]:
            self._draw_character_card(key)

        can_start = self._can_start_selected_character()
        button_color = (70, 170, 90) if can_start else (80, 80, 80)
        arcade.draw_rectangle_filled(
            self.start_button["x"],
            self.start_button["y"],
            self.start_button["w"],
            self.start_button["h"],
            button_color,
        )
        start_label = "Start Run" if can_start else "Locked"
        start_text = arcade.Text(
            start_label,
            self.start_button["x"],
            self.start_button["y"] - 10,
            arcade.color.WHITE,
            18,
            anchor_x="center",
        )
        start_text.draw()
        info_text = arcade.Text(
            "Unlock characters by surviving 10:00 with their prerequisite hero.",
            self.width / 2,
            60,
            arcade.color.LIGHT_GRAY,
            14,
            anchor_x="center",
        )
        info_text.draw()

    def _draw_character_card(self, key: str) -> None:
        definition = self.characters[key]
        rect = self.card_regions[key]
        is_selected = key == self.selected_character
        unlocked = key in self.unlocked_characters
        border_color = definition["color"] if unlocked else (80, 80, 80)
        background = (40, 40, 50)
        arcade.draw_rectangle_filled(rect["x"], rect["y"], rect["w"], rect["h"], background)
        arcade.draw_rectangle_outline(rect["x"], rect["y"], rect["w"], rect["h"], border_color, 3)

        name_text = arcade.Text(
            definition["name"],
            rect["x"],
            rect["y"] + 40,
            arcade.color.WHITE,
            18,
            anchor_x="center",
        )
        name_text.draw()

        blurb_text = arcade.Text(
            definition["blurb"],
            rect["x"] - rect["w"] / 2 + 12,
            rect["y"],
            arcade.color.LIGHT_GRAY,
            12,
            width=rect["w"] - 24,
        )
        blurb_text.draw()

        weapon_names = ", ".join(self._weapon_label(w) for w in sorted(definition["starting_weapons"]))
        weapon_text = arcade.Text(
            f"Starts with: {weapon_names}",
            rect["x"],
            rect["y"] - 22,
            arcade.color.WHITE,
            12,
            anchor_x="center",
        )
        weapon_text.draw()

        if is_selected:
            arcade.draw_rectangle_outline(rect["x"], rect["y"], rect["w"] + 8, rect["h"] + 8, arcade.color.YELLOW, 2)

        if not unlocked:
            arcade.draw_rectangle_filled(rect["x"], rect["y"], rect["w"], rect["h"], (0, 0, 0, 160))
            req = definition.get("unlock")
            requirement = "Survive 10:00" if req else "Unlocked"
            if req:
                prereq_name = self.characters[req["character"]]["name"]
                best_time = self.best_survival_times.get(req["character"], 0)
                requirement = f"Survive 10:00 as {prereq_name}\nBest: {self._format_time_value(best_time)}"
            lock_text = arcade.Text(
                requirement,
                rect["x"],
                rect["y"] - 10,
                arcade.color.LIGHT_GRAY,
                12,
                anchor_x="center",
                align="center",
                width=rect["w"] - 20,
            )
            lock_text.draw()

    def _draw_game_over(self):
        arcade.draw_lrbt_rectangle_filled(0, self.width, 0, self.height, self.menu_background_color)
        headline = arcade.Text(
            "Game Over",
            self.width / 2,
            self.height - 140,
            arcade.color.WHITE,
            36,
            anchor_x="center",
        )
        headline.draw()

        score_text = arcade.Text(
            f"Survival Time: {self._format_time_value(self.last_score)}",
            self.width / 2,
            self.height - 190,
            arcade.color.LIGHT_GRAY,
            18,
            anchor_x="center",
        )
        score_text.draw()

        progress_lines = [
            f"Square best: {self._format_time_value(self.best_survival_times['square'])}",
            f"Triangle best: {self._format_time_value(self.best_survival_times['triangle'])}",
            f"Circle best: {self._format_time_value(self.best_survival_times['circle'])}",
        ]
        for idx, line in enumerate(progress_lines):
            text = arcade.Text(
                line,
                self.width / 2,
                self.height - 230 - idx * 26,
                arcade.color.LIGHT_GRAY,
                14,
                anchor_x="center",
            )
            text.draw()

        arcade.draw_rectangle_filled(
            self.return_button["x"],
            self.return_button["y"],
            self.return_button["w"],
            self.return_button["h"],
            (90, 120, 180),
        )
        return_text = arcade.Text(
            "Return to Start",
            self.return_button["x"],
            self.return_button["y"] - 10,
            arcade.color.WHITE,
            18,
            anchor_x="center",
        )
        return_text.draw()
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

    def _format_elapsed_time(self) -> str:
        minutes = int(self.elapsed_time) // 60
        seconds = int(self.elapsed_time) % 60
        return f"{minutes:02d}:{seconds:02d}"

    def _format_time_value(self, seconds_value: float) -> str:
        minutes = int(seconds_value) // 60
        seconds = int(seconds_value) % 60
        return f"{minutes:02d}:{seconds:02d}"

    def _weapon_label(self, weapon_key: str) -> str:
        names = {
            "projectile": "Straight Shot",
            "orbitals": "Spinning Blades",
            "cardinal": "Spread Burst",
        }
        return names.get(weapon_key, weapon_key)

    def _record_survival_time(self):
        if not self.current_character:
            return
        best = self.best_survival_times.get(self.current_character, 0.0)
        self.best_survival_times[self.current_character] = max(best, self.last_score)

    def _update_unlocks(self):
        # TODO(engine-extraction): Progression/unlocks bucket — survival time ties
        # directly into character availability; isolate from frame update loop.
        if self.current_character:
            best = self.best_survival_times.get(self.current_character, 0.0)
            if self.elapsed_time > best:
                self.best_survival_times[self.current_character] = self.elapsed_time

        if self.best_survival_times.get("square", 0.0) >= 600:
            self.unlocked_characters.add("triangle")
        if self.best_survival_times.get("triangle", 0.0) >= 600:
            self.unlocked_characters.add("circle")

    def handle_game_over(self):
        if self.state != "playing":
            return

        self.last_score = self.elapsed_time
        self._record_survival_time()
        self._update_unlocks()
        self.state = "game_over"

        # Clear active sprites so the next run starts fresh
        self.all_sprites = arcade.SpriteList()
        self.enemies = arcade.SpriteList()
        self.projectiles = arcade.SpriteList()
        self.items = arcade.SpriteList()
        self.player = None
