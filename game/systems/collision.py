import arcade
import math


class CollisionSystem:
    """Handle collision resolution and boundary enforcement for movable sprites."""

    def update(self, world, _dt: float) -> None:
        """Apply pending movements and resolve collisions within the world.

        Args:
            world: Object containing sprite lists, obstacles, and map data.
            _dt: Delta time for the frame (unused for now but kept for parity with
                other systems).
        """
        movers = self._collect_movers(world)
        previous_positions = {sprite: (sprite.center_x, sprite.center_y) for sprite in movers}

        world.all_sprites.update()

        for sprite in movers:
            previous_pos = previous_positions.get(sprite)
            obstacles = world.obstacles if sprite is getattr(world, "player", None) else None
            self.apply_bounds_and_collisions(
                sprite, previous_pos, obstacles=obstacles, game_map=world.map
            )

        self._resolve_enemy_collisions(world, previous_positions)

    def apply_bounds_and_collisions(self, sprite, previous_pos, obstacles, game_map):
        """Clamp sprites to map bounds and prevent passing through obstacles."""
        if previous_pos is None:
            return

        collided = bool(obstacles) and arcade.check_for_collision_with_list(
            sprite, obstacles
        )
        if collided:
            sprite.center_x, sprite.center_y = previous_pos
            sprite.change_x = 0
            sprite.change_y = 0

        self.clamp_to_map(sprite, game_map)

    def clamp_to_map(self, sprite, game_map) -> None:
        """Keep a sprite inside the map rectangle."""
        half_w = sprite.width / 2
        half_h = sprite.height / 2
        clamped_x = min(max(sprite.center_x, half_w), game_map.width - half_w)
        clamped_y = min(max(sprite.center_y, half_h), game_map.height - half_h)

        if clamped_x != sprite.center_x or clamped_y != sprite.center_y:
            sprite.center_x = clamped_x
            sprite.center_y = clamped_y
            sprite.change_x = 0
            sprite.change_y = 0

    def _collect_movers(self, world):
        movers = []
        if getattr(world, "player", None):
            movers.append(world.player)
        movers.extend(getattr(world, "enemies", []))
        return movers

    def _resolve_enemy_collisions(self, world, previous_positions):
        """Separate enemies softly so they pack toward the player without clumping."""

        enemies = getattr(world, "enemies", [])
        if len(enemies) < 2:
            return

        for idx, enemy in enumerate(enemies):
            for other in enemies[idx + 1 :]:
                self._separate_enemies(enemy, other)

    def _separate_enemies(self, a, b) -> None:
        radius_a = getattr(a, "collision_radius", min(a.width, a.height) * 0.5)
        radius_b = getattr(b, "collision_radius", min(b.width, b.height) * 0.5)

        desired_distance = (radius_a + radius_b) * 1.15  # Leave a small buffer between bodies

        dx = b.center_x - a.center_x
        dy = b.center_y - a.center_y
        dist_sq = dx * dx + dy * dy

        # If perfectly overlapping, pick an arbitrary direction to separate
        if dist_sq == 0:
            dx, dy, dist_sq = 1.0, 0.0, 1.0

        if dist_sq >= desired_distance * desired_distance:
            return

        dist = math.sqrt(dist_sq)
        overlap = desired_distance - dist
        nx, ny = dx / dist, dy / dist
        push = overlap * 0.5

        a.center_x -= nx * push
        a.center_y -= ny * push
        b.center_x += nx * push
        b.center_y += ny * push

    def _revert_to_previous(self, sprite, previous_positions):
        if sprite not in previous_positions:
            return
        prev_x, prev_y = previous_positions[sprite]
        sprite.center_x = prev_x
        sprite.center_y = prev_y
        sprite.change_x = 0
        sprite.change_y = 0
