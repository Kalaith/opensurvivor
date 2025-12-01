import arcade
from ..content.weapons.projectile import CardinalProjectile, OrbitingProjectile, Projectile
from ..content.items.experience import ExperienceOrb
from ..content.characters.enemy import ExploderEnemy
from ..core.object_pool import SpriteObjectPool
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


class CombatSystem:
    def __init__(self, engine):
        self.engine = engine
        self.attack_timer = 0.0
        self.base_attack_cooldown = 0.5
        self.orbit_timer = 0.0
        self.orbit_cooldown = 2.0
        self.cardinal_timer = 0.0
        self.cardinal_cooldown = 1.5
        
        # Limit projectiles to prevent performance issues
        self.max_projectiles = 150

        # Object pools for projectiles to reduce allocations
        self.projectile_pools = {
            Projectile: SpriteObjectPool(Projectile, initial_size=50, max_size=500),
            CardinalProjectile: SpriteObjectPool(CardinalProjectile, initial_size=20, max_size=200),
            OrbitingProjectile: SpriteObjectPool(OrbitingProjectile, initial_size=10, max_size=100),
        }

    def update(self, dt: float):
        # Update Projectiles
        expired_projectiles = []
        for proj in self.engine.projectiles:
            # Check if method exists to be safe, or just call it if we are sure
            if hasattr(proj, 'update_projectile'):
                proj.update_projectile(dt)
                # Check if projectile has expired (lifetime <= 0)
                if hasattr(proj, 'lifetime') and proj.lifetime <= 0:
                    expired_projectiles.append(proj)

        # Return expired projectiles to pool
        for proj in expired_projectiles:
            proj_class = proj.__class__
            if proj_class in self.projectile_pools:
                self.projectile_pools[proj_class].release_and_remove_from_lists(
                    proj, [self.engine.projectiles, self.engine.all_sprites]
                )
            else:
                proj.remove_from_sprite_lists()

        # Update Enemies
        throttle_config = None
        if getattr(self.engine, "spawning_system", None):
            throttle_config = getattr(self.engine.spawning_system, "throttle_config", None)

        for enemy in self.engine.enemies:
            if hasattr(enemy, 'update_target'):
                if throttle_config:
                    self._update_enemy_target_with_throttle(enemy, dt, throttle_config)
                else:
                    enemy.update_target(dt)

        # Auto-attack
        player = self.engine.player
        if player and player.has_weapon("projectile"):
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                self.attack_nearest_enemy()
                self.attack_timer = self.get_attack_cooldown()

        # Orbiting blades weapon
        if player and player.has_weapon("orbitals"):
            self.orbit_timer -= dt
            if self.orbit_timer <= 0:
                self.spawn_orbitals()
                self.orbit_timer = self.orbit_cooldown

        # Four-direction burst weapon
        if player and player.has_weapon("cardinal"):
            self.cardinal_timer -= dt
            if self.cardinal_timer <= 0:
                self.fire_cardinal_burst()
                self.cardinal_timer = self.cardinal_cooldown

        # Collisions - Projectiles hit Enemies (using spatial partitioning)
        # Collect sprites to remove to avoid modifying lists during iteration
        projectiles_to_remove = []
        enemies_to_remove = []
        
        # Build quadtree for enemies to enable spatial queries
        enemy_quadtree = self._build_enemy_quadtree()
        
        for proj in self.engine.projectiles:
            # Skip if already marked for removal
            if proj in projectiles_to_remove:
                continue

            # Query nearby enemies instead of checking all enemies
            nearby_enemies = self._query_nearby_enemies(enemy_quadtree, proj)
            hit_enemies = []
            
            for enemy in nearby_enemies:
                if arcade.check_for_collision(proj, enemy):
                    hit_enemies.append(enemy)

            if hit_enemies:
                remaining_pierce = getattr(proj, "pierce", 1)

                for enemy in hit_enemies:
                    # Only process each enemy once per frame
                    if enemy in enemies_to_remove:
                        continue

                    died = False
                    if hasattr(enemy, "take_damage"):
                        died = enemy.take_damage(1, self.engine)
                        self.engine.sound_manager.play("hit")
                    else:
                        died = True

                    if died:
                        enemies_to_remove.append(enemy)
                        # Spawn XP at enemy position
                        orb = ExperienceOrb(enemy.center_x, enemy.center_y)
                        self.engine.items.append(orb)
                        self.engine.all_sprites.append(orb)

                    remaining_pierce -= 1
                    proj.pierce = remaining_pierce
                    if remaining_pierce <= 0:
                        projectiles_to_remove.append(proj)
                        break

                if remaining_pierce > 0 and proj not in projectiles_to_remove:
                    # Allow the projectile to keep flying without removal
                    continue
        
        # Remove all marked sprites
        for proj in projectiles_to_remove:
            # Return projectile to pool instead of just removing from sprite lists
            proj_class = proj.__class__
            if proj_class in self.projectile_pools:
                self.projectile_pools[proj_class].release_and_remove_from_lists(
                    proj, [self.engine.projectiles, self.engine.all_sprites]
                )
            else:
                proj.remove_from_sprite_lists()

        # Enemies hit Player
        player = self.engine.player
        if player:
            hit_enemies = arcade.check_for_collision_with_list(player, self.engine.enemies)
            for enemy in hit_enemies:
                if enemy in enemies_to_remove:
                    continue

                damage = getattr(enemy, "damage", 1)
                player.take_damage(damage)
                self.engine.sound_manager.play("hit")
                if isinstance(enemy, ExploderEnemy):
                    enemies_to_remove.append(enemy)

                if player.health <= 0:
                    print("Player defeated!")
                    self.engine.handle_game_over()
                    break

        for enemy in enemies_to_remove:
            # Return enemy to pool instead of just removing from sprite lists
            if hasattr(self.engine, 'spawning_system') and self.engine.spawning_system:
                enemy_class = enemy.__class__
                if enemy_class in self.engine.spawning_system.enemy_pools:
                    self.engine.spawning_system.enemy_pools[enemy_class].release_and_remove_from_lists(
                        enemy, [self.engine.enemies, self.engine.all_sprites]
                    )
                else:
                    enemy.remove_from_sprite_lists()
            else:
                enemy.remove_from_sprite_lists()

    def attack_nearest_enemy(self):
        if not self.engine.player or not self.engine.enemies:
            return

        # Check projectile limit
        if len(self.engine.projectiles) >= self.max_projectiles:
            return

        # Find nearest enemy
        nearest = None
        min_dist = float('inf')
        px, py = self.engine.player.center_x, self.engine.player.center_y

        for enemy in self.engine.enemies:
            dist = (enemy.center_x - px)**2 + (enemy.center_y - py)**2
            if dist < min_dist:
                min_dist = dist
                nearest = enemy
        
        if nearest:
            dx = nearest.center_x - px
            dy = nearest.center_y - py
            length = (dx**2 + dy**2)**0.5
            if length > 0:
                dx /= length
                dy /= length

                proj = self.projectile_pools[Projectile].get_and_add_to_lists(
                    [self.engine.projectiles, self.engine.all_sprites],
                    px, py, dx, dy,
                    size=self.engine.player.projectile_size,
                    speed=self.engine.player.projectile_speed,
                    lifetime=self.engine.player.projectile_lifetime,
                    pierce=self.engine.player.projectile_pierce,
                )
                self.engine.sound_manager.play("attack")

    def spawn_orbitals(self):
        if not self.engine.player:
            return

        # Check if we have room for 3 more projectiles
        if len(self.engine.projectiles) + 3 > self.max_projectiles:
            return

        # Spawn three blades evenly spaced around the player
        for angle in (0, 120, 240):
            proj = self.projectile_pools[OrbitingProjectile].get_and_add_to_lists(
                [self.engine.projectiles, self.engine.all_sprites],
                self.engine.player
            )
            proj.set_angle(angle)
        self.engine.sound_manager.play("attack")

    def fire_cardinal_burst(self):
        if not self.engine.player:
            return

        # Check if we have room for 4 more projectiles
        if len(self.engine.projectiles) + 4 > self.max_projectiles:
            return

        px, py = self.engine.player.center_x, self.engine.player.center_y
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        for dx, dy in directions:
            proj = self.projectile_pools[CardinalProjectile].get_and_add_to_lists(
                [self.engine.projectiles, self.engine.all_sprites],
                px, py, dx, dy,
                size=self.engine.player.projectile_size,
                speed=self.engine.player.projectile_speed,
                lifetime=self.engine.player.projectile_lifetime,
                pierce=self.engine.player.projectile_pierce,
            )
        self.engine.sound_manager.play("attack")

    def get_attack_cooldown(self) -> float:
        if not self.engine.player:
            return self.base_attack_cooldown
        # Higher multiplier means faster attack speed (shorter cooldown)
        return self.base_attack_cooldown / max(0.1, self.engine.player.attack_speed_multiplier)

    def _update_enemy_target_with_throttle(self, enemy, dt: float, cfg: dict) -> None:
        player = self.engine.player
        if not player:
            enemy.update_target(dt)
            return

        # Track per-enemy stagnation to avoid needless retargeting when nothing
        # is changing in the far field.
        dx = enemy.center_x - enemy.last_pos[0]
        dy = enemy.center_y - enemy.last_pos[1]
        moved_sq = dx * dx + dy * dy
        idle_threshold_sq = cfg.get("idle_distance", 0.0) ** 2
        if moved_sq < idle_threshold_sq:
            enemy.idle_frames += 1
        else:
            enemy.idle_frames = 0
        enemy.last_pos = (enemy.center_x, enemy.center_y)

        dist_x = enemy.center_x - player.center_x
        dist_y = enemy.center_y - player.center_y
        distance_sq = dist_x * dist_x + dist_y * dist_y
        engage_sq = cfg.get("engage_radius", 0.0) ** 2
        near_sq = cfg.get("near_radius", engage_sq) ** 2

        enemy.target_cooldown = max(0.0, enemy.target_cooldown - dt)
        recently_moved = enemy.idle_frames < cfg.get("idle_frame_grace", 0)
        player_close = distance_sq <= near_sq
        actively_engaging = distance_sq <= engage_sq

        if player_close or recently_moved or actively_engaging:
            enemy.target_cooldown = 0.0
            enemy.update_target(dt)
            enemy.target_cooldown = cfg.get("close_interval", cfg.get("minimum_interval", 0.0))
            return

        if enemy.target_cooldown > 0:
            return

        enemy.update_target(dt)
        enemy.target_cooldown = cfg.get("distant_update_interval", 0.3)

    def _build_enemy_quadtree(self) -> _QuadNode:
        """Build a quadtree for spatial enemy queries."""
        map_width = self.engine.map.width
        map_height = self.engine.map.height
        root = _QuadNode(0.0, 0.0, map_width, map_height, depth=0, max_depth=6)
        
        for enemy in self.engine.enemies:
            radius = getattr(enemy, "collision_radius", min(enemy.width, enemy.height) * 0.5)
            root.insert(_QuadItem(enemy, radius))
        
        return root

    def _query_nearby_enemies(self, quadtree: _QuadNode, projectile) -> List[arcade.Sprite]:
        """Query enemies near a projectile using spatial partitioning."""
        # Create a search rectangle around the projectile
        proj_radius = getattr(projectile, "collision_radius", min(projectile.width, projectile.height) * 0.5)
        search_rect = (
            projectile.center_x - proj_radius,
            projectile.center_y - proj_radius,
            proj_radius * 2,
            proj_radius * 2,
        )

        matches: List[_QuadItem] = []
        quadtree.query(search_rect, matches)
        return [item.sprite for item in matches]
