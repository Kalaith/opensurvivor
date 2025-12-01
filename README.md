# Open Survivor

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Arcade](https://img.shields.io/badge/arcade-2.6.17+-orange.svg)](https://api.arcade.academy/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Open Survivor is an open-source, Python-based survivor-like arena game inspired by *Vampire Survivors* and *HoloCure*. Players control a character who automatically attacks while surviving increasingly difficult waves of enemies, collecting experience, and leveling up abilities.

![Gameplay Screenshot](screenshot.png)

## 🎮 Features

### Core Gameplay
- **Top-down Movement:** WASD controls for smooth character movement
- **Auto-Attacking Weapons:** Multiple weapon types with different attack patterns
- **Progressive Difficulty:** Enemy waves that scale over time with elite enemies
- **Experience System:** Collect XP orbs to level up and choose upgrades
- **Multiple Characters:** Unlock different characters with unique starting weapons
- **Upgrade System:** Choose from multiple upgrade options when leveling up

### Weapons & Abilities
- **Projectile:** Straight-shot weapon with pierce and speed upgrades
- **Orbitals:** Spinning blades that orbit around the player
- **Cardinal:** Spread burst firing in all four directions

### Performance Optimizations
- **Spatial Collision Detection:** Quadtree-based collision system for efficient enemy-projectile interactions
- **Object Pooling:** Reusable enemy and projectile pools to reduce memory allocations
- **Sound Pooling:** Limited concurrent audio playback to prevent overload
- **Enemy Throttling:** Distance-based update optimization for distant enemies

## 🏗️ Project Structure

```
opensurvivor/
├── game/                          # Main game package
│   ├── main.py                    # Entry point
│   ├── core/                      # Core engine systems
│   │   ├── engine.py              # Main game engine
│   │   ├── audio.py               # Sound management with pooling
│   │   ├── object_pool.py         # Object pooling system
│   │   └── ...
│   ├── content/                   # Game content
│   │   ├── characters/            # Player and enemy classes
│   │   ├── weapons/               # Weapon implementations
│   │   └── map.py                 # Map definitions
│   ├── systems/                   # Game systems
│   │   ├── combat.py              # Combat and collision logic
│   │   ├── spawning.py            # Enemy spawning system
│   │   ├── leveling.py            # XP and upgrade system
│   │   └── collision.py           # Collision detection
│   └── scenes/                    # Game scenes (menu, gameplay, etc.)
├── tests/                         # Unit tests
├── GDD.md                         # Game Design Document
├── PERFORMANCE_REVIEW.md          # Performance analysis and fixes
├── CODE_REVIEW.md                 # Code quality review
└── README.md
```

## 📋 Requirements

- **Python:** 3.10 or higher
- **Dependencies:** Arcade 2.6.17+ (automatically installed)
- **OS:** Windows, macOS, or Linux

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone https://github.com/Kalaith/opensurvivor.git
cd opensurvivor
```

### 2. Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r game/requirements.txt
```

### 4. Run the Game
```bash
python -m game.main
```

## 🎯 How to Play

### Basic Controls
- **WASD:** Move character
- **Mouse:** Aim (weapons auto-fire toward mouse direction)
- **ESC:** Pause/return to menu

### Gameplay Loop
1. **Survive:** Avoid enemies while they spawn in waves
2. **Collect XP:** Pick up glowing orbs dropped by defeated enemies
3. **Level Up:** Choose upgrades from 3 random options
4. **Unlock Characters:** Survive longer to unlock new characters
5. **Scale Power:** Weapons and abilities grow stronger over time

### Characters
- **Square:** Balanced starter with projectile weapon
- **Triangle:** Orbital blades (unlock after 10 minutes with Square)
- **Circle:** Cardinal spread shots (unlock after 10 minutes with Triangle)

## 🧪 Testing & Development

### Run Tests
```bash
python -m pytest tests/ -v
```

### Testing Hotkeys
Hold **CTRL+SHIFT** for QA commands:
- **F10:** Add 10 minutes to current run timer
- **1/2/3:** Mark characters as having survived 10 minutes (unlocks them)

### Performance Monitoring
The game includes built-in performance optimizations:
- Use `arcade.enable_timings()` for frame rate monitoring
- Check `PERFORMANCE_REVIEW.md` for detailed performance analysis
- Object pools automatically manage memory usage

## 📖 Game Design Document

The `GDD.md` contains detailed game design information. You can inspect its sections programmatically:

```bash
python -m game.game
```

This prints the top-level headings and can be expanded to drive in-game content.

## 🤝 Contributing

Open Survivor is designed to be community-driven and mod-friendly. Areas for contribution:

- **New Weapons:** Add weapon types in `game/content/weapons/`
- **Enemy Types:** Create new enemy behaviors in `game/content/characters/`
- **Maps:** Extend the map system for different arenas
- **UI/UX:** Improve menus and HUD systems
- **Performance:** Optimize systems for better scalability

### Development Guidelines
- Follow the existing code structure and patterns
- Add unit tests for new features
- Update documentation for significant changes
- Test performance impact of changes

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Inspired by *Vampire Survivors* and *HoloCure*
- Built with the excellent [Python Arcade](https://api.arcade.academy/) framework
- Community contributions and feedback welcome!

---

**Happy surviving! 🎮**
