import math
from ...core.entity import Entity


class Projectile(Entity):
    def __init__(
        self,
        x: float,
        y: float,
        dx: float,
        dy: float,
        *,
        size: int = 8,
        speed: float = 400.0,
        lifetime: float = 2.0,
        pierce: int = 1,
        color=(255, 255, 0),
    ):
        # Yellow small square
        super().__init__(x, y, size, size, color)
        self.speed = speed
        self.lifetime = lifetime  # Seconds
        self.pierce = max(1, pierce)

        # Store velocity in pixels per second
        self.vx = dx * self.speed
        self.vy = dy * self.speed

    def update_projectile(self, dt: float):
        self.lifetime -= dt
        # Don't remove from sprite lists here - let the pool system handle it

        # Set velocity with delta_time for smooth movement
        self.change_x = self.vx * dt
        self.change_y = self.vy * dt

    def reset(self):
        """Reset projectile state for reuse from object pool."""
        self.lifetime = 2.0  # Default lifetime
        self.pierce = 1      # Default pierce
        self.change_x = 0
        self.change_y = 0

class CardinalProjectile(Projectile):
    """Projectile that travels in a fixed cardinal direction."""

    def __init__(
        self,
        x: float,
        y: float,
        dx: float,
        dy: float,
        *,
        size: int = 8,
        speed: float = 400.0,
        lifetime: float = 2.0,
        pierce: int = 1,
    ):
        super().__init__(
            x,
            y,
            dx,
            dy,
            size=size,
            speed=speed,
            lifetime=lifetime,
            pierce=pierce,
            color=(255, 165, 0),
        )


class OrbitingProjectile(Entity):
    """Projectile that spins around the player."""

    def __init__(self, player: Entity, angle_degrees: float, radius: float = 60.0):
        # Green small square that stays near the player
        start_rad = math.radians(angle_degrees)
        start_x = player.center_x + math.cos(start_rad) * radius
        start_y = player.center_y + math.sin(start_rad) * radius
        super().__init__(start_x, start_y, 10, 10, (50, 205, 50))

        self.player = player
        self.angle = angle_degrees
        self.radius = radius
        self.angular_speed = 180.0  # Degrees per second
        self.lifetime = 4.0

    def update_projectile(self, dt: float):
        self.lifetime -= dt
        if self.lifetime <= 0 or not self.player:
            # Don't remove from sprite lists here - let the pool system handle it
            return

        self.angle = (self.angle + self.angular_speed * dt) % 360
        rad = math.radians(self.angle)

        target_x = self.player.center_x + math.cos(rad) * self.radius
        target_y = self.player.center_y + math.sin(rad) * self.radius

        # Move towards the target orbit position each frame
        self.change_x = target_x - self.center_x
        self.change_y = target_y - self.center_y

    def reset(self):
        """Reset orbiting projectile state for reuse from object pool."""
        self.lifetime = 4.0
        self.angle = 0
        self.player = None
        self.change_x = 0
        self.change_y = 0
