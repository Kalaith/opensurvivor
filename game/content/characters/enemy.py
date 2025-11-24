from ...core.entity import Entity
import math

class Enemy(Entity):
    def __init__(self, x: float, y: float):
        # Red square for enemy
        super().__init__(x, y, 24, 24, (255, 50, 50))
        self.speed = 100.0
        self.target = None

    def update_target(self, dt: float):
        if self.target:
            # Simple tracking
            dx = self.target.center_x - self.center_x
            dy = self.target.center_y - self.center_y
            
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist > 0:
                dx /= dist
                dy /= dist
                
            # Set velocity with delta_time for smooth movement
            self.change_x = dx * self.speed * dt
            self.change_y = dy * self.speed * dt
