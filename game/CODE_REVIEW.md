# Code Review Notes

## Engine (`game/core/engine.py`)
- `elapsed_time` is initialized twice in `Engine.__init__`. The first assignment before system setup is sufficient; the later one is redundant and may mask future changes to time tracking.
- Movement bounds enforcement relies on `previous_positions` keyed by sprites. If future sprites override equality/`__hash__`, the dictionary could break. Consider switching to an index-based map or storing positions directly on sprites.

## Spawning (`game/systems/spawning.py`)
- `spawn_enemy` ignores the wave profile's configured enemy weights; it hardcodes a fixed distribution instead of using `_select_enemy_class()`. As a result wave definitions don't affect enemy types.

## General
- There are no automated tests. Even small regressions in movement, collisions, and leveling would go unnoticed without manual playtesting. Adding minimal unit or integration checks would help protect core systems.
