import sys
import pathlib

# Ensure the package is in path if run directly
if __name__ == "__main__":
    # Add the parent directory to sys.path
    file_path = pathlib.Path(__file__).resolve()
    root_path = file_path.parents[1]
    if str(root_path) not in sys.path:
        sys.path.append(str(root_path))

# Use absolute imports which are safer when path is set correctly
from game.core.engine import Engine
from game.content.characters.player import Player

def main():
    print("Starting Open Survivor...")
    # Arcade window creation happens in Engine.__init__
    engine = Engine(title="Open Survivor - v0.1")
    
    # Create Player at center of the map bounds
    player = Player(engine.map.width / 2, engine.map.height / 2)
    engine.set_player(player)
    
    engine.start()

if __name__ == "__main__":
    main()
