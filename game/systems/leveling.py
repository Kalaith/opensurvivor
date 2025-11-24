import arcade

class LevelingSystem:
    def __init__(self, engine):
        self.engine = engine

    def update(self, dt: float):
        if not self.engine.player:
            return

        # Check collision with XP orbs
        hits = arcade.check_for_collision_with_list(self.engine.player, self.engine.items)
        for orb in hits:
            self.add_xp(orb.value)
            orb.remove_from_sprite_lists()

    def add_xp(self, amount: int):
        player = self.engine.player
        player.xp += amount
        if player.xp >= player.xp_to_next_level:
            self.level_up()

    def level_up(self):
        player = self.engine.player
        player.xp -= player.xp_to_next_level
        player.level += 1
        player.xp_to_next_level = int(player.xp_to_next_level * 1.2)
        print(f"Level Up! New Level: {player.level}")
        # Trigger upgrade menu here (future)
