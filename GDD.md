# Open Survivor
An open-source, Python-based survivor-like arena game inspired by *Vampire Survivors* and *HoloCure*.

Players control a single character who automatically attacks while surviving waves of enemies, collecting experience, gaining abilities, and scaling power over time.

---

## ✅ Project Goals
- Fully open-source survivor-like game
- Python-based for accessibility and learning
- Modular, extendable architecture
- Community-created content support
- Clean reference implementation for new developers

---

## 🎮 Core Gameplay Loop
1. Player spawns in a map
2. Enemies spawn and move toward the player
3. Player auto-attacks based on weapon cooldowns
4. Player collects experience orbs
5. Level up and choose upgrades
6. Survive increasingly difficult waves
7. Win by surviving the time limit or defeating a boss

**Lose condition:** Player HP reaches 0

---

## 🧱 MVP Features
- Top-down WASD movement
- Auto-attacking weapon
- Enemy waves that scale over time
- XP + level-up system
- Upgrade selection menu (3 choices)
- Single map
- HP bar, XP bar, timer UI
- Basic sound effects

---

## 🚀 Stretch Features (Future)
- Multiple characters with unique starting weapons
- Multiple weapons with evolutions
- Passive items
- Boss enemies with attack patterns
- Additional maps
- Save/load system
- Modding API / plugin system
- Online leaderboard

---

## 🎨 Visual Style
- 2D top-down sprites
- Minimal animation
- Readable silhouettes

Prototype options:
- pixel art
- placeholder shapes
- vector art

---

## 🛠️ Technology
**Language:** Python 3.x  
**Framework:** Pygame (initial choice)

Alternative frameworks:
- Pygame-ce
- Arcade

---

## 🧩 Architecture
Goals:
- Modular systems
- Data-driven content (JSON/YAML)
- Clear separation of:
  - rendering
  - game logic
  - content definitions

### Proposed Folder Structure
open_survivor/
core/
game.py
engine.py
input.py
entity.py
systems/
movement.py
combat.py
spawning.py
content/
weapons/
characters/
enemies/
maps/
assets/
sprites/
sounds/
ui/
tests/


---

## 🕹️ Systems Overview

### Movement
- Player controlled with keyboard
- Enemies track player position

### Combat
Weapons include:
- cooldown
- damage
- projectile pattern
- range

### Upgrades
On level-up, choose 1 of 3 random upgrades, e.g.:
- +20% attack speed
- +1 projectile
- +10% movement speed

### Enemy Waves
- Spawn rate increases over time
- Enemy HP and damage scale
- New enemies appear over time

---

## 🌍 Open Source Goals
- MIT or GPL license (TBD)
- Contribution guidelines
- Plugin-friendly architecture
- Community content packs

---

## 🏁 Milestones

### Milestone 1 – Playable Prototype
- Player movement
- Auto-attack
- Enemy spawning
- XP + leveling

### Milestone 2 – Game Loop
- Upgrade system
- Difficulty scaling
- Win/Lose conditions
- Basic UI

### Milestone 3 – v0.1 Release
- Packaging
- Documentation
- Public repository

---

## 🎯 Target Audience
- Fans of survivor-likes
- Python developers
- Open-source contributors
- Hobbyist game creators

---

## 🤝 Contributing
Contributions will be welcome once the base systems are stable.

Planned contributions:
- weapons
- characters
- enemies
- maps
- balance tuning
