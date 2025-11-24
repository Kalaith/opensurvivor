from ...core.entity import Entity

class Projectile(Entity):
    def __init__(self, x: float, y: float, dx: float, dy: float):
        # Yellow small square
        super().__init__(x, y, 8, 8, (255, 255, 0))
        self.speed = 400.0
        self.lifetime = 2.0 # Seconds
        
        # Store velocity in pixels per second
        self.vx = dx * self.speed
        self.vy = dy * self.speed

    def update_projectile(self, dt: float):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.remove_from_sprite_lists()
            
        # Set velocity with delta_time for smooth movement
        self.change_x = self.vx * dt
        self.change_y = self.vy * dt
