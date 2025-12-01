import arcade
import math


class CollisionSystem:
    """Handle collision resolution and boundary enforcement for movable sprites."""

    def __init__(self):
        self.collision_timer = 0.0
        self.collision_interval = 1 / 60
        self._padding = 1.3  # Spacing multiplier for enemy separation

    def update(self, world, dt: float) -> None:
        """Apply pending movements and resolve collisions within the world.

        Args:
            world: Object containing sprite lists, obstacles, and map data.
            dt: Delta time for the frame.
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

        # Resolve enemy collisions every frame
        self.collision_timer += dt
        if self.collision_timer >= self.collision_interval:
            self.collision_timer = 0.0
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
        """Separate overlapping enemies using Arcade's spatial hash."""
        enemies = getattr(world, "enemies", [])
        if len(enemies) < 2:
            return

        moved = set()
        processed_pairs = set()
        
        # Arcade's SpriteList with use_spatial_hash=True makes this efficient
        # check_for_collision_with_list leverages the spatial hash internally
        for enemy in enemies:
            # Get nearby enemies that are actually colliding (overlapping bounding boxes)
            colliding = arcade.check_for_collision_with_list(enemy, enemies)
            
            for other in colliding:
                # Skip self-collision
                if enemy is other:
                    continue
                
                # Avoid duplicate processing using sorted pair IDs
                pair_id = tuple(sorted([id(enemy), id(other)]))
                if pair_id in processed_pairs:
                    continue
                processed_pairs.add(pair_id)
                    
                if self._separate_pair(enemy, other):
                    moved.add(enemy)
                    moved.add(other)

        # Clamp moved enemies back to map bounds
        for enemy in moved:
            self.clamp_to_map(enemy, world.map)

    def _get_collision_radius(self, sprite):
        """Get the collision radius for a sprite."""
        return getattr(
            sprite, 
            "collision_radius", 
            min(sprite.width, sprite.height) * 0.5
        ) * self._padding

    def _separate_pair(self, a, b) -> bool:
        """Separate two overlapping sprites."""
        radius_a = self._get_collision_radius(a)
        radius_b = self._get_collision_radius(b)
        desired_distance = radius_a + radius_b

        dx = b.center_x - a.center_x
        dy = b.center_y - a.center_y
        dist_sq = dx * dx + dy * dy

        # Handle perfect overlap
        if dist_sq == 0:
            dx, dy = 1.0, 0.0
            dist_sq = 1.0

        # Check if separation is needed
        if dist_sq >= desired_distance * desired_distance:
            return False

        # Separate the sprites
        dist = math.sqrt(dist_sq)
        overlap = desired_distance - dist
        nx, ny = dx / dist, dy / dist
        push = overlap * 0.5

        a.center_x -= nx * push
        a.center_y -= ny * push
        b.center_x += nx * push
        b.center_y += ny * push
        return True
