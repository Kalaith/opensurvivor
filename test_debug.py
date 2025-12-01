import sys
sys.path.insert(0, 'h:\\HatcheryGames\\opensurvivor')
from game.core.audio import SoundManager
from pathlib import Path
import tempfile

print("Testing SoundManager...")
with tempfile.TemporaryDirectory() as tmp:
    sm = SoundManager(Path(tmp))
    sm.load_sounds()
    print('Load successful')