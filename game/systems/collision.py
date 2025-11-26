import arcade


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
        """Prevent enemy sprites from stacking using their circular colliders."""

        enemies = getattr(world, "enemies", [])
        for idx, enemy in enumerate(enemies):
            for other in enemies[idx + 1 :]:
                if self._enemy_circles_overlap(enemy, other):
                    self._revert_to_previous(enemy, previous_positions)
                    self._revert_to_previous(other, previous_positions)

    def _enemy_circles_overlap(self, a, b) -> bool:
        radius_a = getattr(a, "collision_radius", min(a.width, a.height) * 0.5)
        radius_b = getattr(b, "collision_radius", min(b.width, b.height) * 0.5)
        dx = a.center_x - b.center_x
        dy = a.center_y - b.center_y
        return dx * dx + dy * dy < (radius_a + radius_b) ** 2

    def _revert_to_previous(self, sprite, previous_positions):
        if sprite not in previous_positions:
            return
        prev_x, prev_y = previous_positions[sprite]
        sprite.center_x = prev_x
        sprite.center_y = prev_y
        sprite.change_x = 0
        sprite.change_y = 0
