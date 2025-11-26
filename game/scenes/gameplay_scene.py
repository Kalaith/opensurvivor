from __future__ import annotations

import arcade
from typing import TYPE_CHECKING

from .base import BaseScene

if TYPE_CHECKING:
    from game.core.engine import Engine


class GameplayScene(BaseScene):
    def __init__(self, engine: "Engine"):
        self.engine = engine
        self._hud_padding = 20
        self._bar_width = 260
        self._bar_height = 18
        self._time_text = arcade.Text(
            "",
            self._hud_padding,
            self._hud_padding,
            arcade.color.WHITE,
            16,
        )
        self._info_text = arcade.Text(
            "",
            self._hud_padding,
            self._hud_padding + 22,
            arcade.color.LIGHT_GRAY,
            14,
        )
        self._banner_text = arcade.Text(
            "",
            self.engine.width / 2,
            self.engine.height - 40,
            arcade.color.YELLOW,
            18,
            anchor_x="center",
        )
        self._game_over_text = arcade.Text(
            "Game Over",
            self.engine.width / 2,
            self.engine.height - self._hud_padding - 30,
            arcade.color.WHITE,
            28,
            anchor_x="center",
        )

    def on_enter(self) -> None:
        self.engine.paused = False

    def on_exit(self) -> None:
        pass

    def update(self, delta_time: float) -> None:
        if self.engine.paused:
            return

        self.engine.elapsed_time += delta_time
        self.engine.update_unlocks()

        if self.engine.player:
            mx, my = self.engine.input_handler.get_movement_vector()
            self.engine.player.change_x = mx * self.engine.player.speed * delta_time
            self.engine.player.change_y = my * self.engine.player.speed * delta_time
            self.engine.player.regenerate(delta_time)

        self.engine.spawning_system.update(delta_time)
        self.engine.combat_system.update(delta_time)
        self.engine.leveling_system.update(delta_time)

        if self.engine.collision_system:
            self.engine.collision_system.update(self.engine, delta_time)

    def render(self) -> None:
        self._draw_map_background()

        self.engine.obstacles.draw()
        self.engine.all_sprites.draw()

        self._draw_hud()

        notice = self.engine.spawning_system.get_wave_notification()
        if notice:
            self._banner_text.text = notice
            self._banner_text.draw()

        self.engine.leveling_system.draw()

    def handle_key_press(self, key, modifiers) -> None:
        if self.engine.leveling_system.handle_input(key):
            return
        self.engine.input_handler.on_key_press(key, modifiers)

    def handle_key_release(self, key, modifiers) -> None:
        self.engine.input_handler.on_key_release(key, modifiers)

    def handle_mouse_motion(self, x: float, y: float, dx: float, dy: float) -> None:
        self.engine.leveling_system.handle_mouse_motion(x, y, dx, dy)

    def handle_mouse_press(self, x: float, y: float, button, modifiers) -> None:
        if self.engine.leveling_system.handle_mouse_press(x, y, button, modifiers):
            return

    def _draw_map_background(self) -> None:
        arcade.draw_lrbt_rectangle_filled(
            0,
            self.engine.map.width,
            0,
            self.engine.map.height,
            color=self.engine.map.background_color,
        )

        grid_spacing = self.engine.map.grid_spacing
        grid_color = self.engine.map.grid_color
        for x in range(0, int(self.engine.map.width) + 1, grid_spacing):
            arcade.draw_line(x, 0, x, self.engine.map.height, grid_color, 1)
        for y in range(0, int(self.engine.map.height) + 1, grid_spacing):
            arcade.draw_line(0, y, self.engine.map.width, y, grid_color, 1)

    def _draw_hud(self):
        padding = self._hud_padding
        bar_width = self._bar_width
        bar_height = self._bar_height

        self._time_text.text = f"Survival: {self.engine.format_elapsed_time()}"
        self._time_text.anchor_x = "left"
        self._time_text.center_x = padding
        self._time_text.center_y = padding
        self._info_text.anchor_x = "left"
        self._info_text.center_x = padding
        self._info_text.center_y = padding + 22
        enemy_count = len(self.engine.enemies)
        fps_value = arcade.get_fps() or 0.0
        self._info_text.text = f"Enemies: {enemy_count}    FPS: {fps_value:.0f}"

        if self.engine.player and self.engine.player.health > 0:
            hp_ratio = (
                self.engine.player.health / self.engine.player.max_health if self.engine.player.max_health else 0
            )
            xp_ratio = (
                self.engine.player.xp / self.engine.player.xp_to_next_level
                if self.engine.player.xp_to_next_level
                else 0
            )

            hp_y = self.engine.height - padding - bar_height / 2
            xp_y = hp_y - bar_height - 8

            self.engine.draw_bar(
                padding + bar_width / 2,
                hp_y,
                bar_width,
                bar_height,
                hp_ratio,
                (200, 0, 0),
                (60, 20, 20),
                f"HP {self.engine.player.health:.0f}/{self.engine.player.max_health}",
            )

            self.engine.draw_bar(
                padding + bar_width / 2,
                xp_y,
                bar_width,
                bar_height,
                xp_ratio,
                (20, 120, 220),
                (20, 40, 80),
                f"XP {self.engine.player.xp:.0f}/{self.engine.player.xp_to_next_level}",
            )

            self._time_text.draw()
            self._info_text.draw()
        else:
            self._game_over_text.draw()

            self._time_text.center_x = self.engine.width / 2
            self._time_text.center_y = self.engine.height - padding - 70
            self._time_text.anchor_x = "center"
            self._time_text.draw()
            self._info_text.draw()
