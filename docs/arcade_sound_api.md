# Arcade Sound API Reference

## Sound Functions from Quick Index

From https://api.arcade.academy/en/stable/api_docs/quick_index.html

### Core Sound Functions:
- `arcade.load_sound()` - Load a sound file
- `arcade.play_sound()` - Play a sound (returns a player object)
- `arcade.stop_sound()` - Stop a playing sound
- `arcade.Sound` - Sound class

### Usage Pattern:
```python
# Load a sound
sound = arcade.load_sound("path/to/sound.wav")

# Play it
player = arcade.play_sound(sound, volume=0.5)

# Stop it
arcade.stop_sound(player)
```

### Alternative Pattern (from examples):
```python
# Create Sound object directly
sound = arcade.Sound("path/to/sound.wav")

# Play using Sound method
player = sound.play(volume=0.5, speed=1.0)

# Stop using player method
player.stop()

# Check if playing
if player.is_playing():
    # ...
```

## Key Differences

### Old API (may not work):
- `arcade.load_sound()` returns `arcade.Sound`
- Then use `arcade.play_sound(sound)` 

### New API (confirmed working):
- `arcade.Sound(path)` creates sound object
- Then use `sound.play()` method
- Returns player with `.stop()` and `.is_playing()` methods

## Phase 1 Implementation Notes

We use the new API pattern:
1. Load: `arcade.Sound(path)` 
2. Play: `sound.play(volume=X)` returns player
3. Check: `player.is_playing()`
4. Stop: `player.stop()`
