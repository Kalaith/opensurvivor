import arcade
import random
from dataclasses import dataclass
from typing import Callable, List


@dataclass
class UpgradeOption:
    title: str
    description: str
    apply: Callable[[object], None]


class LevelingSystem:
    def __init__(self, engine):
        self.engine = engine
        self.awaiting_choice = False
        self.current_choices: List[UpgradeOption] = []
        self.upgrade_pool = [
            UpgradeOption(
                "Bigger Projectiles",
                "+2 size to projectiles",
                lambda player: setattr(player, "projectile_size", player.projectile_size + 2),
            ),
            UpgradeOption(
                "Faster Projectiles",
                "+15% projectile speed",
                lambda player: setattr(
                    player, "projectile_speed", player.projectile_speed * 1.15
                ),
            ),
            UpgradeOption(
                "More Penetration",
                "+1 enemy pierce",
                lambda player: setattr(
                    player, "projectile_pierce", player.projectile_pierce + 1
                ),
            ),
            UpgradeOption(
                "Shoot Faster",
                "+15% attack speed",
                lambda player: setattr(
                    player,
                    "attack_speed_multiplier",
                    player.attack_speed_multiplier * 1.15,
                ),
            ),
        ]

    def update(self, dt: float):
        if not self.engine.player:
            return

        # Check collision with XP orbs
        hits = arcade.check_for_collision_with_list(self.engine.player, self.engine.items)
        for orb in hits:
            self.add_xp(orb.value)
            self.engine.sound_manager.play("xp_collect")
            orb.remove_from_sprite_lists()

    def add_xp(self, amount: int):
        player = self.engine.player
        player.xp += amount
        while player.xp >= player.xp_to_next_level and not self.awaiting_choice:
            self.level_up()

    def level_up(self):
        player = self.engine.player
        player.xp -= player.xp_to_next_level
        player.level += 1
        player.xp_to_next_level = int(player.xp_to_next_level * 1.2)
        print(f"Level Up! New Level: {player.level}")
        self.present_upgrade_choices()

    def present_upgrade_choices(self):
        if not self.upgrade_pool:
            return

        choices = random.sample(
            self.upgrade_pool, k=min(3, len(self.upgrade_pool))
        )
        self.current_choices = choices
        self.awaiting_choice = True
        self.engine.paused = True
        self.engine.sound_manager.play("level_up")

    def handle_input(self, key):
        if not self.awaiting_choice:
            return False

        keymap = {
            arcade.key.KEY_1: 0,
            arcade.key.NUM_1: 0,
            arcade.key.KEY_2: 1,
            arcade.key.NUM_2: 1,
            arcade.key.KEY_3: 2,
            arcade.key.NUM_3: 2,
        }

        if key in keymap:
            index = keymap[key]
            if index < len(self.current_choices):
                self.apply_choice(index)
                return True
        return False

    def apply_choice(self, index: int):
        if not (0 <= index < len(self.current_choices)):
            return

        choice = self.current_choices[index]
        choice.apply(self.engine.player)
        self.awaiting_choice = False
        self.current_choices = []
        self.engine.paused = False

        # Handle excess XP in case the player banked multiple levels
        player = self.engine.player
        while player.xp >= player.xp_to_next_level and not self.awaiting_choice:
            self.level_up()

    def draw(self):
        if not self.awaiting_choice:
            return

        width, height = self.engine.width, self.engine.height
        arcade.draw_rectangle_filled(
            width / 2, height / 2, width * 0.6, height * 0.5, (0, 0, 0, 200)
        )

        header = arcade.Text(
            "Level Up! Choose an upgrade:", width / 2, height / 2 + 120, anchor_x="center"
        )
        header.draw()

        for i, opt in enumerate(self.current_choices, start=1):
            line = f"{i}. {opt.title} - {opt.description}"
            text = arcade.Text(line, width / 2 - 200, height / 2 + 80 - (i * 40))
            text.draw()

        hint = arcade.Text(
            "Press 1, 2, or 3 to select", width / 2, height / 2 - 140, anchor_x="center"
        )
        hint.draw()
