import arcade

class InputHandler:
    """
    Handles keyboard input using arcade's key constants.
    """
    def __init__(self):
        self.keys_pressed = set()

    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)

    def on_key_release(self, key, modifiers):
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)

    def get_movement_vector(self):
        """
        Returns a normalized (x, y) tuple based on WASD/Arrow keys.
        """
        x, y = 0.0, 0.0

        if arcade.key.W in self.keys_pressed or arcade.key.UP in self.keys_pressed:
            y += 1.0
        if arcade.key.S in self.keys_pressed or arcade.key.DOWN in self.keys_pressed:
            y -= 1.0
        if arcade.key.A in self.keys_pressed or arcade.key.LEFT in self.keys_pressed:
            x -= 1.0
        if arcade.key.D in self.keys_pressed or arcade.key.RIGHT in self.keys_pressed:
            x += 1.0

        length = (x**2 + y**2)**0.5
        if length > 0:
            x /= length
            y /= length
        
        return x, y
