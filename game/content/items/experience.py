from ...core.entity import Entity

class ExperienceOrb(Entity):
    def __init__(self, x: float, y: float, value: int = 10):
        # Green small square
        super().__init__(x, y, 6, 6, (50, 255, 50))
        self.value = value
