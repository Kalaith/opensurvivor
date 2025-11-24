import random
from ..content.characters.enemy import Enemy, ArmoredEnemy, SplittingEnemy

class SpawningSystem:
    def __init__(self, engine):
        self.engine = engine
        self.spawn_timer = 0.0
        self.spawn_rate = 2.0 # Seconds

    def update(self, dt: float):
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_enemy()
            self.spawn_timer = self.spawn_rate
            # Increase difficulty slightly
            self.spawn_rate = max(0.5, self.spawn_rate * 0.98)

    def spawn_enemy(self):
        # Spawn at random edge
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            x = random.uniform(0, self.engine.width)
            y = self.engine.height + 50
        elif side == 'bottom':
            x = random.uniform(0, self.engine.width)
            y = -50
        elif side == 'left':
            x = -50
            y = random.uniform(0, self.engine.height)
        else:
            x = self.engine.width + 50
            y = random.uniform(0, self.engine.height)
        
        enemy_class = random.choices(
            population=[Enemy, SplittingEnemy, ArmoredEnemy],
            weights=[0.6, 0.25, 0.15],
        )[0]

        enemy = enemy_class(x, y)
        enemy.target = self.engine.player
        self.engine.enemies.append(enemy)
        self.engine.all_sprites.append(enemy)
