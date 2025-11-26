import arcade
import math
from collections import defaultdict


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

        self._resolve_enemy_collisions(world)

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

    def _resolve_enemy_collisions(self, world):
        """Separate enemies softly so they pack toward the player without clumping."""

        enemies = getattr(world, "enemies", [])
        if len(enemies) < 2:
            return

        radii = self._cache_radii(enemies)
        cell_size = self._estimate_cell_size(radii)
        buckets = self._bucket_enemies(enemies, cell_size)

        # Only process each pair of neighboring cells once to reduce redundant
        # comparisons when the horde grows large.
        neighbor_offsets = ((0, 0), (1, 0), (0, 1), (1, 1), (1, -1))
        moved = set()

        for (cell_x, cell_y), cell_enemies in buckets.items():
            for dx, dy in neighbor_offsets:
                other_bucket = buckets.get((cell_x + dx, cell_y + dy))
                if not other_bucket:
                    continue

                if dx == 0 and dy == 0:
                    # Only run intra-cell checks once per cell.
                    enemies_to_check = (
                        (cell_enemies[i], cell_enemies[j])
                        for i in range(len(cell_enemies))
                        for j in range(i + 1, len(cell_enemies))
                    )
                else:
                    enemies_to_check = (
                        (enemy, other)
                        for enemy in cell_enemies
                        for other in other_bucket
                    )

                for enemy, other in enemies_to_check:
                    if self._separate_enemies(enemy, other, radii):
                        moved.add(enemy)
                        moved.add(other)

        for enemy in moved:
            self.clamp_to_map(enemy, world.map)

    def _cell_for(self, sprite, cell_size: int) -> tuple[int, int]:
        return int(sprite.center_x // cell_size), int(sprite.center_y // cell_size)

    def _bucket_enemies(self, enemies, cell_size: int):
        buckets = defaultdict(list)
        for enemy in enemies:
            buckets[self._cell_for(enemy, cell_size)].append(enemy)
        return buckets

    def _estimate_cell_size(self, radii: dict) -> int:
        if not radii:
            return 64
        max_diameter = max(radii.values()) * 2
        return max(32, int(max_diameter * 1.2))

    def _cache_radii(self, enemies) -> dict:
        radii = {}
        for enemy in enemies:
            radii[enemy] = getattr(
                enemy, "collision_radius", min(enemy.width, enemy.height) * 0.5
            )
        return radii

    def _separate_enemies(self, a, b, radii=None) -> bool:
        radius_a = (radii or {}).get(
            a, getattr(a, "collision_radius", min(a.width, a.height) * 0.5)
        )
        radius_b = (radii or {}).get(
            b, getattr(b, "collision_radius", min(b.width, b.height) * 0.5)
        )

        desired_distance = (radius_a + radius_b) * 1.15  # Leave a small buffer between bodies

        dx = b.center_x - a.center_x
        dy = b.center_y - a.center_y
        dist_sq = dx * dx + dy * dy

        # If perfectly overlapping, pick an arbitrary direction to separate
        if dist_sq == 0:
            dx, dy, dist_sq = 1.0, 0.0, 1.0

        if dist_sq >= desired_distance * desired_distance:
            return False

        dist = math.sqrt(dist_sq)
        overlap = desired_distance - dist
        nx, ny = dx / dist, dy / dist
        push = overlap * 0.5

        a.center_x -= nx * push
        a.center_y -= ny * push
        b.center_x += nx * push
        b.center_y += ny * push
        return True

    def _revert_to_previous(self, sprite, previous_positions):
        if sprite not in previous_positions:
            return
        prev_x, prev_y = previous_positions[sprite]
        sprite.center_x = prev_x
        sprite.center_y = prev_y
        sprite.change_x = 0
        sprite.change_y = 0
