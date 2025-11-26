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
        previous_positions = [(sprite.center_x, sprite.center_y) for sprite in movers]

        world.all_sprites.update()

        for sprite, previous_pos in zip(movers, previous_positions):
            obstacles = world.obstacles if sprite is getattr(world, "player", None) else None
            self.apply_bounds_and_collisions(
                sprite, previous_pos, obstacles=obstacles, game_map=world.map
            )

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
