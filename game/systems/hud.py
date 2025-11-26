from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import arcade


@dataclass
class PlayerHUDData:
    """Snapshot of player stats needed for HUD rendering."""

    health: float
    max_health: float
    xp: float
    xp_to_next_level: float


class HUDSystem:
    """Responsible for rendering the in-game heads-up display."""

    def __init__(self, padding: int = 20, bar_width: int = 260, bar_height: int = 18) -> None:
        self.padding = padding
        self.bar_width = bar_width
        self.bar_height = bar_height

    def draw(
        self,
        *,
        window_size: Tuple[float, float],
        elapsed_time: float,
        player: PlayerHUDData | None,
    ) -> None:
        width, height = window_size
        padding = self.padding
        bar_width = self.bar_width
        bar_height = self.bar_height

        time_text = arcade.Text(
            f"Survival: {self._format_time_value(elapsed_time)}",
            padding,
            padding,
            arcade.color.WHITE,
            16,
        )

        if player and player.health > 0:
            hp_ratio = player.health / player.max_health if player.max_health else 0
            xp_ratio = (
                player.xp / player.xp_to_next_level if player.xp_to_next_level else 0
            )

            hp_y = height - padding - bar_height / 2
            xp_y = hp_y - bar_height - 8

            self._draw_bar(
                padding + bar_width / 2,
                hp_y,
                bar_width,
                bar_height,
                hp_ratio,
                (200, 0, 0),
                (60, 20, 20),
                f"HP {player.health:.0f}/{player.max_health}",
            )

            self._draw_bar(
                padding + bar_width / 2,
                xp_y,
                bar_width,
                bar_height,
                xp_ratio,
                (20, 120, 220),
                (20, 40, 80),
                f"XP {player.xp:.0f}/{player.xp_to_next_level}",
            )

            time_text.draw()
            return

        game_over = arcade.Text(
            "Game Over",
            width / 2,
            height - padding - 30,
            arcade.color.WHITE,
            28,
            anchor_x="center",
        )
        game_over.draw()

        time_text.center_x = width / 2
        time_text.center_y = height - padding - 70
        time_text.anchor_x = "center"
        time_text.draw()

    def _draw_bar(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        ratio: float,
        fill_color: tuple[int, int, int],
        background_color: tuple[int, int, int],
        label: str,
    ) -> None:
        clamped_ratio = max(0.0, min(1.0, ratio))
        arcade.draw_lbwh_rectangle_filled(x - width / 2, y - height / 2, width, height, background_color)

        filled_width = width * clamped_ratio
        left = x - width / 2
        if filled_width > 0:
            arcade.draw_lbwh_rectangle_filled(
                left, y - height / 2, filled_width, height, fill_color
            )

        text = arcade.Text(label, left + 6, y - height / 2 + 2, arcade.color.WHITE, 12)
        text.draw()

    @staticmethod
    def _format_time_value(seconds_value: float) -> str:
        minutes = int(seconds_value) // 60
        seconds = int(seconds_value) % 60
        return f"{minutes:02d}:{seconds:02d}"
