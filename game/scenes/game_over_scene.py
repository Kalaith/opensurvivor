from __future__ import annotations

import arcade
from typing import TYPE_CHECKING

from .base import BaseScene

if TYPE_CHECKING:
    from game.core.engine import Engine


class GameOverScene(BaseScene):
    def __init__(self, engine: "Engine"):
        self.engine = engine

    def on_enter(self) -> None:
        pass

    def on_exit(self) -> None:
        pass

    def update(self, delta_time: float) -> None:
        return

    def render(self) -> None:
        self._draw_game_over()

    def handle_key_press(self, key, modifiers) -> None:
        return

    def handle_key_release(self, key, modifiers) -> None:
        return

    def handle_mouse_motion(self, x: float, y: float, dx: float, dy: float) -> None:
        return

    def handle_mouse_press(self, x: float, y: float, button, modifiers) -> None:
        self._handle_game_over_click(x, y)

    def _handle_game_over_click(self, x: float, y: float) -> None:
        if (
            abs(x - self.engine.return_button["x"]) <= self.engine.return_button["w"] / 2
            and abs(y - self.engine.return_button["y"]) <= self.engine.return_button["h"] / 2
        ):
            self.engine.return_to_menu()

    def _draw_game_over(self):
        arcade.draw_lrbt_rectangle_filled(0, self.engine.width, 0, self.engine.height, self.engine.menu_background_color)
        headline = arcade.Text(
            "Game Over",
            self.engine.width / 2,
            self.engine.height - 140,
            arcade.color.WHITE,
            36,
            anchor_x="center",
        )
        headline.draw()

        score_text = arcade.Text(
            f"Survival Time: {self.engine.format_time_value(self.engine.last_score)}",
            self.engine.width / 2,
            self.engine.height - 190,
            arcade.color.LIGHT_GRAY,
            18,
            anchor_x="center",
        )
        score_text.draw()

        progress_lines = [
            f"Square best: {self.engine.format_time_value(self.engine.best_survival_times['square'])}",
            f"Triangle best: {self.engine.format_time_value(self.engine.best_survival_times['triangle'])}",
            f"Circle best: {self.engine.format_time_value(self.engine.best_survival_times['circle'])}",
        ]
        for idx, line in enumerate(progress_lines):
            text = arcade.Text(
                line,
                self.engine.width / 2,
                self.engine.height - 230 - idx * 26,
                arcade.color.LIGHT_GRAY,
                14,
                anchor_x="center",
            )
            text.draw()

        arcade.draw_lbwh_rectangle_filled(
            self.engine.return_button["x"] - self.engine.return_button["w"] / 2,
            self.engine.return_button["y"] - self.engine.return_button["h"] / 2,
            self.engine.return_button["w"],
            self.engine.return_button["h"],
            (90, 120, 180),
        )
        return_text = arcade.Text(
            "Return to Start",
            self.engine.return_button["x"],
            self.engine.return_button["y"] - 10,
            arcade.color.WHITE,
            18,
            anchor_x="center",
        )
        return_text.draw()
