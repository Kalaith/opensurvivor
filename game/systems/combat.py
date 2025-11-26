import arcade
from ..content.weapons.projectile import CardinalProjectile, OrbitingProjectile, Projectile
from ..content.items.experience import ExperienceOrb
from ..content.characters.enemy import ExploderEnemy

class CombatSystem:
    def __init__(self, engine):
        self.engine = engine
        self.attack_timer = 0.0
        self.base_attack_cooldown = 0.5
        self.orbit_timer = 0.0
        self.orbit_cooldown = 2.0
        self.cardinal_timer = 0.0
        self.cardinal_cooldown = 1.5

    def update(self, dt: float):
        # Update Projectiles
        for proj in self.engine.projectiles:
            # Check if method exists to be safe, or just call it if we are sure
            if hasattr(proj, 'update_projectile'):
                proj.update_projectile(dt)

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

        # Collisions - Projectiles hit Enemies
        # Collect sprites to remove to avoid modifying lists during iteration
        projectiles_to_remove = []
        enemies_to_remove = []
        
        for proj in self.engine.projectiles:
            # Skip if already marked for removal
            if proj in projectiles_to_remove:
                continue

            hit_enemies = arcade.check_for_collision_with_list(proj, self.engine.enemies)
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
            enemy.remove_from_sprite_lists()

    def attack_nearest_enemy(self):
        if not self.engine.player or not self.engine.enemies:
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

                proj = Projectile(
                    px,
                    py,
                    dx,
                    dy,
                    size=self.engine.player.projectile_size,
                    speed=self.engine.player.projectile_speed,
                    lifetime=self.engine.player.projectile_lifetime,
                    pierce=self.engine.player.projectile_pierce,
                )
                self.engine.projectiles.append(proj)
                self.engine.all_sprites.append(proj)
                self.engine.sound_manager.play("attack")

    def spawn_orbitals(self):
        if not self.engine.player:
            return

        # Spawn three blades evenly spaced around the player
        for angle in (0, 120, 240):
            proj = OrbitingProjectile(self.engine.player, angle)
            self.engine.projectiles.append(proj)
            self.engine.all_sprites.append(proj)
        self.engine.sound_manager.play("attack")

    def fire_cardinal_burst(self):
        if not self.engine.player:
            return

        px, py = self.engine.player.center_x, self.engine.player.center_y
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        for dx, dy in directions:
            proj = CardinalProjectile(
                px,
                py,
                dx,
                dy,
                size=self.engine.player.projectile_size,
                speed=self.engine.player.projectile_speed,
                lifetime=self.engine.player.projectile_lifetime,
                pierce=self.engine.player.projectile_pierce,
            )
            self.engine.projectiles.append(proj)
            self.engine.all_sprites.append(proj)
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
