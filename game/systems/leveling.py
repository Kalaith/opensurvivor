import arcade
import random
from dataclasses import dataclass
from typing import Callable, List, Tuple


@dataclass
class UpgradeOption:
    title: str
    description: str
    apply: Callable[[object], None]
    icon: str = ""
    tooltip: str = ""


class LevelingSystem:
    def __init__(self, engine):
        self.engine = engine
        self.awaiting_choice = False
        self.current_choices: List[UpgradeOption] = []
        self.option_boxes: List[Tuple[float, float, float, float]] = []
        self.last_mouse_pos: Tuple[float, float] = (0.0, 0.0)
        self.feedback_message: str = ""
        self.feedback_timer: float = 0.0

        self.upgrade_sound = arcade.load_sound(":resources:sounds/upgrade5.wav")

        def grow_projectiles(player):
            player.projectile_size += 2

        def accelerate_projectiles(player):
            player.projectile_speed *= 1.15

        def pierce_more(player):
            player.projectile_pierce += 1

        def attack_faster(player):
            player.attack_speed_multiplier *= 1.15

        def bolster_health(player):
            player.max_health += 25
            player.health = min(player.max_health, player.health + 25)

        def regenerative_surplus(player):
            player.regen_rate *= 1.3
            player.regen_cooldown = max(0.5, player.regen_cooldown - 0.5)

        def swift_stride(player):
            player.speed *= 1.1

        self.upgrade_pool = [
            UpgradeOption(
                "Bigger Projectiles",
                "+2 size to projectiles",
                grow_projectiles,
                icon="⬤",
                tooltip="Projectiles occupy more space, improving hits.",
            ),
            UpgradeOption(
                "Faster Projectiles",
                "+15% projectile speed",
                accelerate_projectiles,
                icon="➹",
                tooltip="Shots reach targets sooner.",
            ),
            UpgradeOption(
                "More Penetration",
                "+1 enemy pierce",
                pierce_more,
                icon="↪",
                tooltip="Bullets carry through another foe.",
            ),
            UpgradeOption(
                "Shoot Faster",
                "+15% attack speed",
                attack_faster,
                icon="⚡",
                tooltip="Shorter delays between shots.",
            ),
            UpgradeOption(
                "Fortified Frame",
                "+25 max HP and heal 25",
                bolster_health,
                icon="❤",
                tooltip="Stay in the fight longer with extra vitality.",
            ),
            UpgradeOption(
                "Regenerative Surge",
                "+30% regen rate, -0.5s regen delay",
                regenerative_surplus,
                icon="✚",
                tooltip="Healing ramps up sooner after damage.",
            ),
            UpgradeOption(
                "Fleet Footing",
                "+10% movement speed",
                swift_stride,
                icon="➤",
                tooltip="Cover ground and dodge threats faster.",
            ),
        ]

    def update(self, dt: float):
        if self.feedback_timer > 0:
            self.feedback_timer = max(0.0, self.feedback_timer - dt)

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
        self.option_boxes = []
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

    def handle_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        self.last_mouse_pos = (x, y)

    def handle_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        if not self.awaiting_choice:
            return False

        if button != arcade.MOUSE_BUTTON_LEFT:
            return False

        for idx, box in enumerate(self.option_boxes):
            if self._point_in_box(x, y, box):
                self.apply_choice(idx)
                return True

        return False

    def apply_choice(self, index: int):
        if not (0 <= index < len(self.current_choices)):
            return

        choice = self.current_choices[index]
        choice.apply(self.engine.player)
        arcade.play_sound(self.upgrade_sound)
        self.feedback_message = f"{choice.title} applied!"
        self.feedback_timer = 1.6
        self.awaiting_choice = False
        self.current_choices = []
        self.engine.paused = False

        # Handle excess XP in case the player banked multiple levels
        player = self.engine.player
        while player.xp >= player.xp_to_next_level and not self.awaiting_choice:
            self.level_up()

    def draw(self):
        width, height = self.engine.width, self.engine.height

        if self.awaiting_choice:
            panel_width, panel_height = width * 0.7, height * 0.65
            panel_x, panel_y = width / 2, height / 2
            self.option_boxes = []

            arcade.draw_lbwh_rectangle_filled(
                panel_x - width / 2, panel_y - height / 2, width, height, (10, 10, 25, 180)
            )
            arcade.draw_lbwh_rectangle_filled(
                panel_x - panel_width / 2, panel_y - panel_height / 2, panel_width, panel_height, (25, 28, 45, 230)
            )
            arcade.draw_lbwh_rectangle_outline(
                panel_x - panel_width / 2, panel_y - panel_height / 2, panel_width, panel_height, (120, 180, 255, 255), 4
            )

            header = arcade.Text(
                "Level Up!", panel_x, panel_y + panel_height / 2 - 60, (230, 241, 255), 34, anchor_x="center"
            )
            subheader = arcade.Text(
                "Choose an upgrade to power up.",
                panel_x,
                panel_y + panel_height / 2 - 95,
                (195, 209, 255),
                18,
                anchor_x="center",
            )
            header.draw()
            subheader.draw()

            option_height = 110
            option_spacing = 16
            top_y = panel_y + panel_height / 2 - 140

            for i, opt in enumerate(self.current_choices):
                option_center_y = top_y - i * (option_height + option_spacing)
                left = panel_x - panel_width / 2 + 40
                right = panel_x + panel_width / 2 - 40
                bottom = option_center_y - option_height / 2
                top = option_center_y + option_height / 2
                box = (left, bottom, right, top)
                self.option_boxes.append(box)

                is_hovered = self._point_in_box(*self.last_mouse_pos, box)
                bg_color = (50, 60, 90, 230) if is_hovered else (38, 44, 70, 210)
                arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, bg_color)
                arcade.draw_lbwh_rectangle_outline(
                    left, bottom, right - left, top - bottom, (150, 200, 255, 255), 2
                )

                badge_text = arcade.Text(
                    f"{i + 1}", left + 14, option_center_y, (255, 255, 255), 16, anchor_y="center"
                )
                badge_radius = 18
                arcade.draw_circle_filled(
                    left + badge_radius, option_center_y, badge_radius, (90, 125, 255, 255)
                )
                badge_text.draw()

                title = arcade.Text(
                    f"{opt.icon} {opt.title}",
                    left + 46,
                    option_center_y + 28,
                    (255, 255, 255),
                    20,
                    bold=True,
                )
                description = arcade.Text(
                    opt.description,
                    left + 46,
                    option_center_y,
                    (207, 224, 255),
                    15,
                )
                tooltip = arcade.Text(
                    opt.tooltip or "Click or press number to select",
                    left + 46,
                    option_center_y - 24,
                    (159, 180, 228),
                    13,
                )

                title.draw()
                description.draw()
                tooltip.draw()

            hint = arcade.Text(
                "Click or press 1, 2, or 3 to select an upgrade",
                panel_x,
                panel_y - panel_height / 2 + 40,
                (230, 241, 255),
                16,
                anchor_x="center",
            )
            hint.draw()
        else:
            self.option_boxes = []

        if self.feedback_timer > 0 and self.feedback_message:
            feedback = arcade.Text(
                self.feedback_message,
                width / 2,
                height - 40,
                (216, 243, 220),
                18,
                anchor_x="center",
                bold=True,
            )
            shadow = arcade.Text(
                self.feedback_message,
                width / 2 + 2,
                height - 42,
                (0, 0, 0, 180),
                18,
                anchor_x="center",
                bold=True,
            )
            shadow.draw()
            feedback.draw()

    def _point_in_box(self, x: float, y: float, box: Tuple[float, float, float, float]) -> bool:
        left, bottom, right, top = box
        return left <= x <= right and bottom <= y <= top
