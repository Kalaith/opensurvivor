from __future__ import annotations

import arcade

from ..systems.hud import HUDSystem, PlayerHUDData


class GameplayScene:
    """Handles rendering during active gameplay."""

    def __init__(self, engine, hud_system: HUDSystem) -> None:
        self.engine = engine
        self.hud_system = hud_system

    def draw(self) -> None:
        engine = self.engine
        engine._draw_map_background()

        engine.obstacles.draw()
        engine.all_sprites.draw()

        player_data = None
        if engine.player:
            player = engine.player
            player_data = PlayerHUDData(
                health=player.health,
                max_health=player.max_health,
                xp=player.xp,
                xp_to_next_level=player.xp_to_next_level,
            )

        self.hud_system.draw(
            window_size=(engine.width, engine.height),
            elapsed_time=engine.elapsed_time,
            player=player_data,
        )

        notice = engine.spawning_system.get_wave_notification()
        if notice:
            banner = arcade.Text(
                notice,
                engine.width / 2,
                engine.height - 40,
                arcade.color.YELLOW,
                18,
                anchor_x="center",
            )
            banner.draw()

        engine.leveling_system.draw()


class GameOverScene:
    """Renders the end-of-run summary screen."""

    def __init__(self, engine) -> None:
        self.engine = engine

    def draw(self) -> None:
        engine = self.engine
        arcade.draw_lrbt_rectangle_filled(
            0, engine.width, 0, engine.height, engine.menu_background_color
        )
        headline = arcade.Text(
            "Game Over",
            engine.width / 2,
            engine.height - 140,
            arcade.color.WHITE,
            36,
            anchor_x="center",
        )
        headline.draw()

        score_text = arcade.Text(
            f"Survival Time: {engine._format_time_value(engine.last_score)}",
            engine.width / 2,
            engine.height - 190,
            arcade.color.LIGHT_GRAY,
            18,
            anchor_x="center",
        )
        score_text.draw()

        progress_lines = [
            f"Square best: {engine._format_time_value(engine.best_survival_times['square'])}",
            f"Triangle best: {engine._format_time_value(engine.best_survival_times['triangle'])}",
            f"Circle best: {engine._format_time_value(engine.best_survival_times['circle'])}",
        ]
        for idx, line in enumerate(progress_lines):
            text = arcade.Text(
                line,
                engine.width / 2,
                engine.height - 230 - idx * 26,
                arcade.color.LIGHT_GRAY,
                14,
                anchor_x="center",
            )
            text.draw()

        arcade.draw_rectangle_filled(
            engine.return_button["x"],
            engine.return_button["y"],
            engine.return_button["w"],
            engine.return_button["h"],
            (90, 120, 180),
        )
        return_text = arcade.Text(
            "Return to Start",
            engine.return_button["x"],
            engine.return_button["y"] - 10,
            arcade.color.WHITE,
            18,
            anchor_x="center",
        )
        return_text.draw()
