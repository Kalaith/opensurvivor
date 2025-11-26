import arcade
import math
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class _QuadItem:
    sprite: arcade.Sprite
    radius: float

    @property
    def bounds(self) -> Tuple[float, float, float, float]:
        diameter = self.radius * 2
        return (
            self.sprite.center_x - self.radius,
            self.sprite.center_y - self.radius,
            diameter,
            diameter,
        )


class _QuadNode:
    """Lightweight quadtree node for broad-phase collision pruning."""

    def __init__(self, x: float, y: float, w: float, h: float, depth: int, max_depth: int, capacity: int = 8):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.depth = depth
        self.max_depth = max_depth
        self.capacity = capacity
        self.items: List[_QuadItem] = []
        self.children: Optional[Tuple['_QuadNode', '_QuadNode', '_QuadNode', '_QuadNode']] = None

    def insert(self, item: _QuadItem) -> None:
        if self.children:
            child = self._child_for(item)
            if child:
                child.insert(item)
                return

        self.items.append(item)

        # Only subdivide once per node; items that straddle boundaries stay here.
        if (
            not self.children
            and len(self.items) > self.capacity
            and self.depth < self.max_depth
        ):
            self._subdivide()

    def query(self, rect: Tuple[float, float, float, float], results: List[_QuadItem]) -> None:
        if not self._intersects(rect, (self.x, self.y, self.w, self.h)):
            return

        results.extend(self.items)
        if not self.children:
            return

        for child in self.children:
            child.query(rect, results)

    def _child_for(self, item: _QuadItem) -> Optional['_QuadNode']:
        if not self.children:
            return None

        cx = item.sprite.center_x
        cy = item.sprite.center_y
        half_w = self.w * 0.5
        half_h = self.h * 0.5

        in_left = cx + item.radius <= self.x + half_w
        in_right = cx - item.radius >= self.x + half_w
        in_bottom = cy + item.radius <= self.y + half_h
        in_top = cy - item.radius >= self.y + half_h

        # If the circle straddles the split, keep it here to avoid missed pairs.
        if not ((in_left or in_right) and (in_bottom or in_top)):
            return None

        index = 0
        if in_right:
            index += 1
        if in_top:
            index += 2
        return self.children[index]

    def _subdivide(self) -> None:
        half_w = self.w * 0.5
        half_h = self.h * 0.5
        next_depth = self.depth + 1
        self.children = (
            _QuadNode(self.x, self.y, half_w, half_h, next_depth, self.max_depth, self.capacity),
            _QuadNode(self.x + half_w, self.y, half_w, half_h, next_depth, self.max_depth, self.capacity),
            _QuadNode(self.x, self.y + half_h, half_w, half_h, next_depth, self.max_depth, self.capacity),
            _QuadNode(self.x + half_w, self.y + half_h, half_w, half_h, next_depth, self.max_depth, self.capacity),
        )

        # Re-insert existing items so they settle into child nodes where possible.
        current_items = self.items
        self.items = []
        for item in current_items:
            self.insert(item)

    @staticmethod
    def _intersects(a: Tuple[float, float, float, float], b: Tuple[float, float, float, float]) -> bool:
        ax, ay, aw, ah = a
        bx, by, bw, bh = b
        return not (ax + aw < bx or bx + bw < ax or ay + ah < by or by + bh < ay)


class CollisionSystem:
    """Handle collision resolution and boundary enforcement for movable sprites."""

    # Limit the number of neighbor interactions per enemy to avoid quadratic blow-up
    # when hundreds of bodies pile onto the player.
    _MAX_NEIGHBORS = 12

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
        quad_root = self._build_quadtree(enemies, radii, world.map.width, world.map.height)
        max_radius = max(radii.values())

        moved = set()
        for enemy in enemies:
            search_radius = (radii[enemy] + max_radius) * 1.2
            candidates = self._query_quadtree(quad_root, enemy, search_radius)

            if len(candidates) > self._MAX_NEIGHBORS:
                candidates = self._closest_neighbors(enemy, candidates)

            for other in candidates:
                if enemy is other or id(enemy) >= id(other):
                    continue
                if self._separate_enemies(enemy, other, radii):
                    moved.add(enemy)
                    moved.add(other)

        for enemy in moved:
            self.clamp_to_map(enemy, world.map)

    def _build_quadtree(self, enemies, radii: dict, width: float, height: float) -> _QuadNode:
        root = _QuadNode(0.0, 0.0, width, height, depth=0, max_depth=6)
        for enemy in enemies:
            root.insert(_QuadItem(enemy, radii[enemy]))
        return root

    def _query_quadtree(self, root: _QuadNode, sprite, radius: float) -> List[arcade.Sprite]:
        search_rect = (
            sprite.center_x - radius,
            sprite.center_y - radius,
            radius * 2,
            radius * 2,
        )

        matches: List[_QuadItem] = []
        root.query(search_rect, matches)
        return [item.sprite for item in matches]

    def _cache_radii(self, enemies) -> dict:
        radii = {}
        for enemy in enemies:
            radii[enemy] = getattr(
                enemy, "collision_radius", min(enemy.width, enemy.height) * 0.5
            )
        return radii

    def _closest_neighbors(self, sprite, candidates):
        """Return only the nearest candidates to reduce pair resolution cost."""

        distances = []
        sx, sy = sprite.center_x, sprite.center_y
        for other in candidates:
            dx = other.center_x - sx
            dy = other.center_y - sy
            # Use squared distance to avoid sqrt until separation time.
            distances.append((dx * dx + dy * dy, other))

        distances.sort(key=lambda item: item[0])
        limited = [item[1] for item in distances[: self._MAX_NEIGHBORS]]
        return limited

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
