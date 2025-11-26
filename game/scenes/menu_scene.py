from __future__ import annotations

import arcade
from typing import TYPE_CHECKING

from .base import BaseScene

if TYPE_CHECKING:
    from game.core.engine import Engine


class MenuScene(BaseScene):
    def __init__(self, engine: "Engine"):
        self.engine = engine

    def on_enter(self) -> None:
        pass

    def on_exit(self) -> None:
        pass

    def update(self, delta_time: float) -> None:
        # Menu has no background updates yet.
        return

    def render(self) -> None:
        self._draw_menu()

    def handle_key_press(self, key, modifiers) -> None:
        return

    def handle_key_release(self, key, modifiers) -> None:
        return

    def handle_mouse_motion(self, x: float, y: float, dx: float, dy: float) -> None:
        return

    def handle_mouse_press(self, x: float, y: float, button, modifiers) -> None:
        self._handle_menu_click(x, y)

    def _handle_menu_click(self, x: float, y: float) -> None:
        for key, rect in self.engine.card_regions.items():
            if abs(x - rect["x"]) <= rect["w"] / 2 and abs(y - rect["y"]) <= rect["h"] / 2:
                self.engine.selected_character = key
                break

        if not self._can_start_selected_character():
            return

        if (
            abs(x - self.engine.start_button["x"]) <= self.engine.start_button["w"] / 2
            and abs(y - self.engine.start_button["y"]) <= self.engine.start_button["h"] / 2
        ):
            self.engine.start_game(self.engine.selected_character)

    def _can_start_selected_character(self) -> bool:
        return self.engine.selected_character in self.engine.unlocked_characters

    def _draw_menu(self):
        arcade.draw_lrbt_rectangle_filled(0, self.engine.width, 0, self.engine.height, self.engine.menu_background_color)

        title = arcade.Text(
            "Open Survivor",
            self.engine.width / 2,
            self.engine.height - 120,
            arcade.color.WHITE,
            36,
            anchor_x="center",
        )
        subtitle = arcade.Text(
            "Choose your character to begin",
            self.engine.width / 2,
            self.engine.height - 170,
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
            self.engine.start_button["x"],
            self.engine.start_button["y"],
            self.engine.start_button["w"],
            self.engine.start_button["h"],
            button_color,
        )
        start_label = "Start Run" if can_start else "Locked"
        start_text = arcade.Text(
            start_label,
            self.engine.start_button["x"],
            self.engine.start_button["y"] - 10,
            arcade.color.WHITE,
            18,
            anchor_x="center",
        )
        start_text.draw()
        info_text = arcade.Text(
            "Unlock characters by surviving 10:00 with their prerequisite hero.",
            self.engine.width / 2,
            60,
            arcade.color.LIGHT_GRAY,
            14,
            anchor_x="center",
        )
        info_text.draw()

    def _draw_character_card(self, key: str) -> None:
        definition = self.engine.characters[key]
        rect = self.engine.card_regions[key]
        is_selected = key == self.engine.selected_character
        unlocked = key in self.engine.unlocked_characters
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

        weapon_names = ", ".join(self.engine.weapon_label(w) for w in sorted(definition["starting_weapons"]))
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
                prereq_name = self.engine.characters[req["character"]]["name"]
                best_time = self.engine.best_survival_times.get(req["character"], 0)
                requirement = f"Survive 10:00 as {prereq_name}\nBest: {self.engine.format_time_value(best_time)}"
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
