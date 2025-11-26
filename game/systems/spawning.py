import random
from ..content.characters.enemy import Enemy, ArmoredEnemy, ExploderEnemy, SplittingEnemy

class SpawningSystem:
    def __init__(self, engine):
        self.engine = engine
        self.spawn_timer = 0.0
        self.wave_profiles = [
            {
                "start": 0,
                "spawn_rate": 2.0,
                "weights": [
                    (Enemy, 0.7),
                    (SplittingEnemy, 0.15),
                    (ArmoredEnemy, 0.1),
                    (ExploderEnemy, 0.05),
                ],
                "elite_chance": 0.0,
                "max_enemies": 25,
                "label": "Warm-up",
            },
            {
                "start": 60,
                "spawn_rate": 1.5,
                "weights": [
                    (Enemy, 0.55),
                    (SplittingEnemy, 0.2),
                    (ArmoredEnemy, 0.2),
                    (ExploderEnemy, 0.05),
                ],
                "elite_chance": 0.1,
                "max_enemies": 35,
                "label": "Pressure Rising",
            },
            {
                "start": 120,
                "spawn_rate": 1.1,
                "weights": [
                    (Enemy, 0.4),
                    (SplittingEnemy, 0.28),
                    (ArmoredEnemy, 0.22),
                    (ExploderEnemy, 0.1),
                ],
                "elite_chance": 0.2,
                "max_enemies": 45,
                "label": "Elite Threats",
            },
            {
                "start": 180,
                "spawn_rate": 0.9,
                "weights": [
                    (Enemy, 0.35),
                    (SplittingEnemy, 0.27),
                    (ArmoredEnemy, 0.28),
                    (ExploderEnemy, 0.1),
                ],
                "elite_chance": 0.3,
                "max_enemies": 55,
                "label": "Overwhelming Odds",
            },
        ]
        self.current_wave_index = -1
        self.current_profile = None
        self.spawn_rate = 2.0
        self.max_enemies = 40
        self.wave_notification_timer = 0.0
        self.wave_message = ""
        self.elite_health_multiplier = 2.0
        self.elite_speed_multiplier = 1.15
        self.scaled_elite_chance = 0.0
        self._update_wave_profile(force=True)

    def update(self, dt: float):
        self._update_wave_profile()
        self.wave_notification_timer = max(0.0, self.wave_notification_timer - dt)

        if len(self.engine.enemies) >= self.max_enemies:
            self.spawn_timer = 0.0
            return

        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_enemy()
            self.spawn_timer = self.spawn_rate

    def spawn_enemy(self):
        # Spawn at random edge
        side = random.choice(['top', 'bottom', 'left', 'right'])
        map_width = self.engine.map.width
        map_height = self.engine.map.height
        if side == 'top':
            x = random.uniform(0, map_width)
            y = map_height + 50
        elif side == 'bottom':
            x = random.uniform(0, map_width)
            y = -50
        elif side == 'left':
            x = -50
            y = random.uniform(0, map_height)
        else:
            x = map_width + 50
            y = random.uniform(0, map_height)
        
        enemy_class = self._select_enemy_class()

        enemy = enemy_class(x, y)
        enemy.target = self.engine.player
        self._scale_enemy(enemy)
        self._apply_elite_modifiers(enemy)
        self.engine.enemies.append(enemy)
        self.engine.all_sprites.append(enemy)

    def _select_enemy_class(self):
        if not self.current_profile:
            return Enemy
        population = [enemy for enemy, _ in self.current_profile["weights"]]
        weights = [weight for _, weight in self.current_profile["weights"]]
        return random.choices(population=population, weights=weights)[0]

    def _apply_elite_modifiers(self, enemy):
        if random.random() > self.scaled_elite_chance:
            return

        enemy.health = int(enemy.health * self.elite_health_multiplier)
        enemy.speed *= self.elite_speed_multiplier
        if hasattr(enemy, "color"):
            # Handle both 3-tuple (RGB) and 4-tuple (RGBA)
            c = enemy.color
            r, g, b = c[0], c[1], c[2]
            enemy.color = (min(255, int(r * 0.8)), min(255, int(g * 0.8)), min(255, int(b * 1.2)))
        enemy.is_elite = True

    def _update_wave_profile(self, force: bool = False):
        elapsed = getattr(self.engine, "elapsed_time", 0.0)
        minutes_elapsed = elapsed / 60.0
        new_index = self.current_wave_index
        for idx, profile in enumerate(self.wave_profiles):
            if elapsed >= profile["start"]:
                new_index = idx
        if force or new_index != self.current_wave_index:
            self.current_wave_index = new_index
            self.current_profile = self.wave_profiles[new_index]
            self.wave_message = f"Wave {self.current_wave_index + 1}: {self.current_profile.get('label', 'Unknown')}"
            self.wave_notification_timer = 3.0
            print(self.wave_message)

        self._apply_difficulty_scaling(minutes_elapsed)

    def get_wave_status(self) -> str:
        if not self.current_profile:
            return "Wave 0"
        label = self.current_profile.get("label", "")
        elite = int(self.current_profile.get("elite_chance", 0.0) * 100)
        return f"Wave {self.current_wave_index + 1}: {label} (rate {self.spawn_rate:.2f}s, elite {elite}%)"

    def get_wave_notification(self):
        if self.wave_notification_timer <= 0:
            return None
        return self.wave_message

    def _apply_difficulty_scaling(self, minutes_elapsed: float) -> None:
        """Continuously tighten spawn cadence and enemy strength."""
        if not self.current_profile:
            return

        base_spawn_rate = self.current_profile["spawn_rate"]
        # Shrink spawn intervals exponentially so late-game floods the arena.
        spawn_rate_multiplier = 0.85 ** minutes_elapsed
        self.spawn_rate = max(0.05, base_spawn_rate * spawn_rate_multiplier)

        base_max = self.current_profile.get("max_enemies", self.max_enemies)
        self.max_enemies = base_max + int(minutes_elapsed * 20)

        # Make elites both more common and vastly stronger over time.
        base_elite_chance = self.current_profile.get("elite_chance", 0.0)
        self.scaled_elite_chance = min(0.95, base_elite_chance + minutes_elapsed * 0.02)
        self.elite_health_multiplier = 2.0 + minutes_elapsed * 1.5
        self.elite_speed_multiplier = 1.15 + minutes_elapsed * 0.05

    def _scale_enemy(self, enemy: Enemy) -> None:
        """Ramp core stats with survival time to ensure eventual defeat."""
        elapsed = getattr(self.engine, "elapsed_time", 0.0)
        minutes_elapsed = elapsed / 60.0

        health_multiplier = 1.0 + minutes_elapsed * 3.0
        speed_multiplier = 1.0 + minutes_elapsed * 0.12
        damage_multiplier = 1.0 + minutes_elapsed * 4.0

        enemy.health = max(1, int(enemy.health * health_multiplier))
        enemy.speed *= speed_multiplier
        if hasattr(enemy, "damage"):
            enemy.damage = int(enemy.damage * damage_multiplier)
