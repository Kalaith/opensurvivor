import arcade
from ..content.weapons.projectile import CardinalProjectile, OrbitingProjectile, Projectile
from ..content.items.experience import ExperienceOrb

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
        for enemy in self.engine.enemies:
            if hasattr(enemy, 'update_target'):
                enemy.update_target(dt)

        # Auto-attack
        self.attack_timer -= dt
        if self.attack_timer <= 0:
            self.attack_nearest_enemy()
            self.attack_timer = self.get_attack_cooldown()

        # Orbiting blades weapon
        self.orbit_timer -= dt
        if self.orbit_timer <= 0:
            self.spawn_orbitals()
            self.orbit_timer = self.orbit_cooldown

        # Four-direction burst weapon
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
                enemies_to_remove.append(enemy)

                if player.health <= 0:
                    print("Player defeated!")
                    self.engine.close()
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

    def spawn_orbitals(self):
        if not self.engine.player:
            return

        # Spawn three blades evenly spaced around the player
        for angle in (0, 120, 240):
            proj = OrbitingProjectile(self.engine.player, angle)
            self.engine.projectiles.append(proj)
            self.engine.all_sprites.append(proj)

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

    def get_attack_cooldown(self) -> float:
        if not self.engine.player:
            return self.base_attack_cooldown
        # Higher multiplier means faster attack speed (shorter cooldown)
        return self.base_attack_cooldown / max(0.1, self.engine.player.attack_speed_multiplier)
