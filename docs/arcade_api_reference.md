# Arcade API Reference

Complete API documentation for Python Arcade library components used in this project.

## Table of Contents

1. [Window and View](#window-and-view)
2. [Sprites](#sprites)
3. [Sprite Lists](#sprite-lists)
4. [Sound](#sound)
5. [Texture Management](#texture-management)
6. [Drawing Primitives](#drawing-primitives)
7. [Physics Engines](#physics-engines)
8. [Text](#text)
9. [Camera 2D](#camera-2d)
10. [Geometry](#geometry)
11. [Utility Functions](#utility)
12. [Types](#types)

---

## Window and View

### arcade.Window
Main game window class with event handling.

**Constructor:**
```python
arcade.Window(
    width=800,
    height=600,
    title="Arcade Window",
    fullscreen=False,
    resizable=False,
    update_rate=1/60,
    antialiasing=True
)
```

**Key Properties:**
- `background_color` - RGBA tuple for window background
- `center` - Center point of the window
- `ctx` - OpenGL context
- `current_view` - Currently active View
- `keyboard` - KeyStateHandler for input

**Event Methods:**
- `on_draw()` - Called when window needs to be redrawn
- `on_update(delta_time)` - Called to update game logic
- `on_key_press(symbol, modifiers)` - Key press events
- `on_key_release(symbol, modifiers)` - Key release events
- `on_mouse_press(x, y, button, modifiers)` - Mouse button press
- `on_mouse_release(x, y, button, modifiers)` - Mouse button release
- `on_mouse_motion(x, y, dx, dy)` - Mouse movement

**Key Functions:**
- `open_window()` - Create and open a window
- `get_window()` - Get the current window instance
- `set_window()` - Set the active window
- `close_window()` - Close the window
- `run()` - Start the event loop
- `exit()` - Exit the application
- `schedule(function, interval)` - Schedule repeated function calls
- `unschedule(function)` - Remove scheduled function

### arcade.View
Container for separate game screens/states.

**Key Methods:**
- `on_draw()` - Draw the view
- `on_update(delta_time)` - Update logic
- `on_show_view()` - Called when view becomes active
- `on_hide_view()` - Called when view is hidden
- Event handlers (same as Window)

**Usage:**
```python
class MyView(arcade.View):
    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)
    
    def on_draw(self):
        self.clear()
        # Draw code here
    
    def on_update(self, delta_time):
        # Update logic here
        pass

window = arcade.Window(800, 600, "My Game")
view = MyView()
window.show_view(view)
arcade.run()
```

### arcade.Section
Divide window into sections with separate drawing.

**Constructor:**
```python
arcade.Section(
    left, bottom, width, height,
    draw_order=0,
    enabled=True
)
```

---

## Sprites

### arcade.Sprite
Full-featured sprite with rotation, textures, physics.

**Constructor:**
```python
arcade.Sprite(
    path_or_texture=None,
    scale=1.0,
    center_x=0,
    center_y=0,
    angle=0
)
```

**Position Properties:**
- `position` - (x, y) tuple
- `center_x`, `center_y` - Center position
- `left`, `right`, `top`, `bottom` - Edges
- `angle` - Rotation in degrees

**Appearance Properties:**
- `width`, `height` - Dimensions in pixels
- `scale` - Size multiplier
- `color` - RGBA tuple
- `alpha` - Transparency (0-255)
- `visible` - Boolean visibility
- `texture` - Current texture

**Movement Properties:**
- `change_x`, `change_y` - Velocity
- `change_angle` - Rotation velocity

**Collision:**
- `hit_box` - Points defining collision shape
- `collides_with_sprite(other)` - Check collision with sprite
- `collides_with_list(sprite_list)` - Check collisions with list
- `collides_with_point(point)` - Check point collision

**Movement Methods:**
- `update(delta_time)` - Update position by velocity
- `update_animation(delta_time)` - Update texture animation
- `forward(speed)` - Move forward
- `reverse(speed)` - Move backward
- `turn_left(theta)` - Rotate left
- `turn_right(theta)` - Rotate right
- `stop()` - Set velocities to 0

**Example:**
```python
sprite = arcade.Sprite(":resources:images/player.png", scale=0.5)
sprite.center_x = 400
sprite.center_y = 300
sprite.change_x = 3  # Move right at 3 pixels/frame
```

### arcade.BasicSprite
Minimal sprite without rotation/hitbox modification.

**Constructor:**
```python
arcade.BasicSprite(
    texture,
    scale=1.0,
    center_x=0,
    center_y=0,
    visible=True
)
```

### arcade.SpriteSolidColor
Create sprite from solid color.

```python
arcade.SpriteSolidColor(width, height, color)
```

### arcade.SpriteCircle
Create circular sprite.

```python
arcade.SpriteCircle(radius, color, soft=False)
```

### Texture Animation

**arcade.TextureKeyframe:**
```python
TextureKeyframe(texture, duration=100)
```

**arcade.TextureAnimation:**
```python
animation = TextureAnimation([keyframe1, keyframe2, ...])
```

**arcade.TextureAnimationSprite:**
Sprite that plays texture animations with time-based frame selection.

---

## Sprite Lists

### arcade.SpriteList
Batch drawing optimization for sprites.

**Constructor:**
```python
arcade.SpriteList(
    use_spatial_hash=False,
    spatial_hash_cell_size=128,
    atlas=None,
    capacity=100,
    lazy=False,
    visible=True
)
```

**Spatial Hash:**
- Enables O(1) collision detection for static sprites
- O(N) update cost when sprites move
- Critical for performance with many sprites

**Key Methods:**
- `append(sprite)` - Add sprite to list
- `remove(sprite)` - Remove sprite
- `pop(index=-1)` - Remove and return sprite
- `clear(capacity=None, deep=True)` - Remove all sprites
- `draw()` - Draw all sprites
- `update(delta_time)` - Update all sprites

**Collision Detection:**
- `check_for_collision_with_list(sprite, sprite_list, method=0)` - Check sprite against list
- `get_sprites_at_point(point, sprite_list)` - Get sprites at point

**Properties:**
- `alpha` - Transparency for all sprites
- `color` - Color for all sprites
- `visible` - Visibility of entire list
- `center` - Center point of all sprites
- `spatial_hash` - Access to spatial hash (if enabled)

**Performance:**
- Can handle tens of thousands of sprites
- Uses GPU batch rendering
- Lazy initialization delays OpenGL resources until draw()

**Example:**
```python
# Create sprite list with spatial hash for collision optimization
enemies = arcade.SpriteList(use_spatial_hash=True)

# Add sprites
for i in range(100):
    enemy = arcade.Sprite("enemy.png")
    enemy.center_x = i * 50
    enemy.center_y = 300
    enemies.append(enemy)

# Draw all at once (GPU optimized)
enemies.draw()

# Update all
enemies.update(delta_time)

# Check collisions (O(1) with spatial hash)
hits = arcade.check_for_collision_with_list(player, enemies)
```

---

## Sound

### arcade.Sound
Class for loading and playing audio.

**Constructor:**
```python
sound = arcade.Sound(file_name, streaming=False)
```

**Streaming Mode:**
- `streaming=True` saves memory BUT disables:
  - Looping
  - Simultaneous playback of same sound
- Use streaming for music, not for sound effects

**Methods:**
```python
player = sound.play(volume=1.0, pan=0.0, loop=False, speed=1.0)
```
- Returns `pyglet.media.Player` object
- `volume`: 0.0 to 1.0
- `pan`: -1.0 (left) to 1.0 (right)
- `loop`: True for continuous playback
- `speed`: Playback speed multiplier

**Player Methods:**
```python
player.is_playing()  # Returns bool
player.stop()        # Stop playback
player.volume        # Get/set volume
```

**Helper Functions:**
```python
# Load sound (same as Sound constructor)
sound = arcade.load_sound(path, streaming=False)

# Play sound directly
player = arcade.play_sound(sound, volume=1.0, pan=0.0, loop=False, speed=1.0)

# Stop player
arcade.stop_sound(player)

# Check if playing
is_playing = arcade.is_playing(player)

# Get/set volume
volume = arcade.get_volume(player)
arcade.set_volume(volume, player)
```

**Audio Formats:**
- **Most reliable:** WAV, OGG (cross-platform)
- See pyglet media documentation for full format list

**Example:**
```python
# Load sound effect
laser = arcade.Sound(":resources:sounds/laser1.wav")

# Play with volume
player = laser.play(volume=0.5)

# Check if still playing
if player.is_playing():
    print("Sound is playing")

# Stop early
player.stop()

# Load music with streaming
music = arcade.Sound("background_music.ogg", streaming=True)
music_player = music.play(volume=0.3, loop=True)
```

---

## Texture Management

### arcade.Texture
Wrapper for image data, hit boxes, and transformations.

**Constructor:**
```python
texture = arcade.Texture(
    image,  # PIL Image or ImageData
    hit_box_algorithm=None,
    hit_box_points=None,
    hash=None
)
```

**Properties:**
- `width`, `height` - Virtual dimensions
- `size` - (width, height) tuple
- `image` - PIL Image object
- `hit_box_points` - Collision points
- `hit_box_algorithm` - Algorithm used for hitbox
- `file_path` - Path to source file (if loaded from file)
- `properties` - Dict for custom metadata

**Transformation Methods:**
```python
# Flipping
new_tex = texture.flip_horizontally()
new_tex = texture.flip_vertically()
new_tex = texture.flip_left_right()
new_tex = texture.flip_top_bottom()
new_tex = texture.flip_diagonally()

# Rotation
new_tex = texture.rotate_90(count=1)
new_tex = texture.rotate_180()
new_tex = texture.rotate_270()

# Transpose
new_tex = texture.transpose()
new_tex = texture.transverse()

# Cropping
new_tex = texture.crop(x, y, width, height)
```

**Static Methods:**
```python
# Create empty texture
texture = arcade.Texture.create_empty(
    name="my_texture",
    size=(64, 64),
    color=(255, 255, 255, 255),
    hit_box_points=None
)
```

### Loading Textures

**arcade.load_texture:**
```python
texture = arcade.load_texture(
    file_path,
    hit_box_algorithm=None,
    hash=None
)
```

**Example:**
```python
# Load texture
texture = arcade.load_texture(":resources:images/player.png")
texture = arcade.load_texture("my_image.png")
texture = arcade.load_texture(Path("assets/sprite.png"))

# Load with custom hitbox algorithm
from arcade.hitbox import algo_detailed
texture = arcade.load_texture(
    "enemy.png",
    hit_box_algorithm=algo_detailed
)
```

### Loading Images

**arcade.load_image:**
```python
image = arcade.load_image(file_path, mode='RGBA')
```
Returns PIL Image for manipulation before creating texture.

### Sprite Sheets

**arcade.load_spritesheet:**
```python
sheet = arcade.load_spritesheet(file_name)

# Get individual texture
texture = sheet.get_texture(
    rect=arcade.Rect(x, y, width, height),
    hit_box_algorithm=None,
    y_up=False
)

# Get grid of textures
textures = sheet.get_texture_grid(
    size=(32, 32),
    columns=8,
    count=64,
    margin=(0, 0, 0, 0),  # left, right, bottom, top
    hit_box_algorithm=None
)
```

### Texture Generation

**arcade.make_circle_texture:**
```python
texture = arcade.make_circle_texture(
    diameter=64,
    color=(255, 0, 0, 255),
    name=None,
    hit_box_algorithm=None
)
```

**arcade.make_soft_circle_texture:**
```python
texture = arcade.make_soft_circle_texture(
    diameter=64,
    color=(255, 0, 0, 255),
    center_alpha=255,
    outer_alpha=0,
    name=None,
    hit_box_algorithm=None
)
```

**arcade.make_soft_square_texture:**
```python
texture = arcade.make_soft_square_texture(
    size=64,
    color=(255, 0, 0, 255),
    center_alpha=255,
    outer_alpha=0,
    name=None
)
```

---

## Drawing Primitives

All drawing functions support RGBA color tuples or Color instances.

### Points

```python
# Draw single point
arcade.draw_point(x, y, color, size=1.0)

# Draw multiple points
arcade.draw_points(point_list, color, size=1.0)
```

### Lines

```python
# Single line
arcade.draw_line(start_x, start_y, end_x, end_y, color, line_width=1)

# Multiple separate lines (pairs of points)
arcade.draw_lines(point_list, color, line_width=1)

# Connected line strip
arcade.draw_line_strip(point_list, color, line_width=1)
```

### Circles

```python
# Filled circle
arcade.draw_circle_filled(
    center_x, center_y, radius,
    color,
    tilt_angle=0,
    num_segments=-1
)

# Circle outline
arcade.draw_circle_outline(
    center_x, center_y, radius,
    color,
    border_width=1,
    tilt_angle=0,
    num_segments=-1
)
```

### Ellipses

```python
# Filled ellipse
arcade.draw_ellipse_filled(
    center_x, center_y, width, height,
    color,
    tilt_angle=0,
    num_segments=-1
)

# Ellipse outline
arcade.draw_ellipse_outline(
    center_x, center_y, width, height,
    color,
    border_width=1,
    tilt_angle=0,
    num_segments=-1
)
```

### Rectangles

```python
# Filled rectangle (using Rect)
arcade.draw_rect_filled(rect, color, tilt_angle=0)

# Rectangle outline (using Rect)
arcade.draw_rect_outline(rect, color, border_width=1, tilt_angle=0)

# LRBT rectangle (left, right, bottom, top)
arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, color)
arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, color, border_width=1)

# LBWH rectangle (left, bottom, width, height)
arcade.draw_lbwh_rectangle_filled(left, bottom, width, height, color)
arcade.draw_lbwh_rectangle_outline(left, bottom, width, height, color, border_width=1)
```

### Triangles

```python
# Filled triangle
arcade.draw_triangle_filled(x1, y1, x2, y2, x3, y3, color)

# Triangle outline
arcade.draw_triangle_outline(
    x1, y1, x2, y2, x3, y3,
    color,
    border_width=1
)
```

### Polygons

```python
# Filled polygon
arcade.draw_polygon_filled(point_list, color)

# Polygon outline
arcade.draw_polygon_outline(point_list, color, line_width=1)
```

### Arcs

```python
# Filled arc (pie slice)
arcade.draw_arc_filled(
    center_x, center_y, width, height,
    color,
    start_angle, end_angle,
    tilt_angle=0,
    num_segments=128
)

# Arc outline
arcade.draw_arc_outline(
    center_x, center_y, width, height,
    color,
    start_angle, end_angle,
    border_width=1,
    tilt_angle=0,
    num_segments=128
)
```

### Parabolas

```python
# Filled parabola
arcade.draw_parabola_filled(
    start_x, start_y, end_x, height,
    color,
    tilt_angle=0
)

# Parabola outline
arcade.draw_parabola_outline(
    start_x, start_y, end_x, height,
    color,
    border_width=1,
    tilt_angle=0
)
```

### Textures and Sprites

```python
# Draw texture on rectangle
arcade.draw_texture_rect(
    texture, rect,
    color=(255, 255, 255, 255),
    angle=0.0,
    blend=True,
    alpha=255,
    pixelated=False,
    atlas=None
)

# Draw sprite
arcade.draw_sprite(
    sprite,
    blend=True,
    alpha=255,
    pixelated=False,
    atlas=None
)

# Draw sprite at specific rect
arcade.draw_sprite_rect(
    sprite, rect,
    blend=True,
    alpha=255,
    pixelated=False,
    atlas=None
)
```

---

## Physics Engines

### PhysicsEngineSimple
Basic top-down physics.

**Constructor:**
```python
engine = arcade.PhysicsEngineSimple(
    player_sprite,
    walls=None  # SpriteList or list of SpriteLists
)
```

**Usage:**
```python
# Create engine
engine = arcade.PhysicsEngineSimple(player, walls)

# Update (in on_update)
engine.update()  # Returns list of colliding sprites

# Properties
engine.player_sprite  # The player
engine.walls  # List of wall SpriteLists
```

### PhysicsEnginePlatformer
Platformer physics with gravity.

**Constructor:**
```python
engine = arcade.PhysicsEnginePlatformer(
    player_sprite,
    platforms=None,
    gravity_constant=0.5,
    ladders=None,
    walls=None
)
```

**Properties:**
- `gravity_constant` - Downward acceleration (default 0.5)
- `allow_multi_jump` - Enable air jumps
- `allowed_jumps` - Total jumps allowed (including first)
- `jumps_since_ground` - Current jump count
- `player_sprite` - The player sprite
- `platforms` - Moving platforms
- `walls` - Static terrain
- `ladders` - Climbable sprites

**Methods:**
```python
# Jump
engine.jump(velocity)

# Jump checking
can_jump = engine.can_jump(y_distance=5)
is_on_ladder = engine.is_on_ladder()

# Multi-jump
engine.enable_multi_jump(allowed_jumps=2)
engine.disable_multi_jump()
engine.increment_jump_counter()

# Update
colliding_sprites = engine.update()
```

**Platform Auto-Movement:**
Set these on platform sprites:
```python
# Horizontal movement
platform.change_x = 2
platform.boundary_left = 100
platform.boundary_right = 400

# Vertical movement
platform.change_y = 1
platform.boundary_bottom = 100
platform.boundary_top = 300
```

### PymunkPhysicsEngine
Advanced physics with Pymunk/Chipmunk2D.

**Constructor:**
```python
engine = arcade.PymunkPhysicsEngine(
    gravity=(0, -900),
    damping=1.0,
    maximum_incline_on_ground=0.708
)
```

**Body Types:**
- `DYNAMIC` (0) - Controlled by forces/impulses
- `KINEMATIC` (1) - Controlled by velocity/position
- `STATIC` (2) - Non-moving terrain

**Adding Sprites:**
```python
engine.add_sprite(
    sprite,
    mass=1.0,
    friction=0.2,
    elasticity=None,
    moment_of_inertia=None,
    body_type=DYNAMIC,
    damping=None,
    gravity=None,
    max_velocity=None,
    max_horizontal_velocity=None,
    max_vertical_velocity=None,
    radius=0,
    collision_type=None
)

# Add multiple sprites
engine.add_sprite_list(sprite_list, **kwargs)
```

**Force/Velocity Control:**
```python
# Apply force (for DYNAMIC bodies)
engine.apply_force(sprite, force=(100, 0))

# Apply impulse (instant force)
engine.apply_impulse(sprite, impulse=(50, 100))

# Set velocity (for KINEMATIC bodies)
engine.set_velocity(sprite, velocity=(100, 0))
engine.set_horizontal_velocity(sprite, 100)

# Set position
engine.set_position(sprite, position=(400, 300))

# Set rotation
engine.set_rotation(sprite, rotation=45)

# Set friction
engine.set_friction(sprite, friction=0.8)
```

**Collision Handlers:**
```python
def begin_handler(arbiter, space, data):
    # Called when collision begins
    return True  # Return False to reject collision

def pre_handler(arbiter, space, data):
    # Called before collision resolution
    return True

def post_handler(arbiter, space, data):
    # Called after collision resolution
    pass

def separate_handler(arbiter, space, data):
    # Called when sprites separate
    pass

engine.add_collision_handler(
    "player", "enemy",
    begin_handler=begin_handler,
    pre_handler=pre_handler,
    post_handler=post_handler,
    separate_handler=separate_handler
)
```

**Query Methods:**
```python
# Check if on ground
is_grounded = engine.is_on_ground(sprite)

# Get grounding info
grounding = engine.check_grounding(sprite)

# Get physics object for sprite
physics_obj = engine.get_physics_object(sprite)

# Get sprite from shape
sprite = engine.get_sprite_for_shape(shape)

# Get sprites from collision arbiter
sprite1, sprite2 = engine.get_sprites_from_arbiter(arbiter)
```

**Update:**
```python
# Step the physics simulation
engine.step(
    delta_time=1/60,
    resync_sprites=True  # Sync visual sprites to physics
)

# Multiple sub-steps per frame
for _ in range(3):
    engine.step(delta_time=1/180, resync_sprites=False)
engine.step(delta_time=1/180, resync_sprites=True)
```

**Remove Sprite:**
```python
engine.remove_sprite(sprite)
```

---

## Text

### arcade.Text
Object-oriented text drawing (FAST).

**Constructor:**
```python
text_obj = arcade.Text(
    text="Hello",
    x=100, y=100, z=0,
    color=(255, 255, 255, 255),
    font_size=12,
    width=None,
    align="left",  # "left", "center", "right"
    font_name="Arial",
    bold=False,
    italic=False,
    anchor_x="left",  # "left", "center", "right"
    anchor_y="baseline",  # "top", "bottom", "center", "baseline"
    multiline=False,
    rotation=0,
    batch=None,
    group=None
)
```

**Properties (all writable):**
```python
text_obj.value = "New text"  # or .text
text_obj.x = 200
text_obj.y = 300
text_obj.position = (200, 300)
text_obj.color = arcade.color.RED
text_obj.font_size = 16
text_obj.rotation = 45
text_obj.visible = True
```

**Drawing:**
```python
# Draw single text
text_obj.draw()

# Batch drawing (FASTEST for multiple text objects)
from pyglet.graphics import Batch

batch = Batch()
text1 = arcade.Text("Text 1", 0, 50, batch=batch)
text2 = arcade.Text("Text 2", 0, 100, batch=batch)
text3 = arcade.Text("Text 3", 0, 150, batch=batch)

# Draw all at once
batch.draw()

# Remove from batch
text2.batch = None
```

**Efficient Updates:**
```python
# Update multiple properties efficiently
with text_obj:
    text_obj.value = "New text"
    text_obj.color = arcade.color.BLUE
    text_obj.font_size = 20
```

**Utility Methods:**
```python
# Convert between em and pixels
pixels = text_obj.em_to_px(2.5)  # 2.5em to pixels
ems = text_obj.px_to_em(30)  # 30px to ems

# Get content size
width = text_obj.content_width
height = text_obj.content_height
size = text_obj.content_size  # (width, height)

# Get bounds
rect = text_obj.rect
left = text_obj.left
right = text_obj.right
top = text_obj.top
bottom = text_obj.bottom

# Debug drawing
text_obj.draw_debug(
    anchor_color=(255, 0, 0, 255),
    background_color=(0, 255, 0, 128),
    outline_color=(0, 0, 255, 255)
)
```

### arcade.draw_text
Simple but SLOW text drawing.

```python
arcade.draw_text(
    text="Hello",
    x=100, y=100, z=0,
    color=(255, 255, 255, 255),
    font_size=12,
    width=None,
    align="left",
    font_name="Arial",
    bold=False,
    italic=False,
    anchor_x="left",
    anchor_y="baseline",
    multiline=False,
    rotation=0
)
```

⚠️ **Warning:** This function is very slow. Use `arcade.Text` for better performance.

### Loading Fonts

```python
# Load custom font
arcade.load_font("path/to/font.ttf")
arcade.load_font(":resources:fonts/custom.ttf")

# Then use by name
text = arcade.Text("Hello", 100, 100, font_name="CustomFontName")
```

### Creating Text Sprites

```python
sprite = arcade.create_text_sprite(
    text="Score: 100",
    color=(255, 255, 255, 255),
    font_size=24,
    width=None,
    align="left",
    font_name="Arial",
    bold=False,
    italic=False,
    anchor_x="left",
    multiline=False,
    background_color=None,  # Transparent by default
    texture_atlas=None
)

# Add to sprite list and draw like any sprite
ui_sprites.append(sprite)
```

---

## Camera 2D

(Documentation will be added after fetching camera_2d.html)

---

## Geometry

(Documentation will be added after fetching geometry.html)

---

## Utility

(Documentation will be added after fetching utility.html)

---

## Types

(Documentation will be added after fetching types.html)

---

## Key Patterns and Best Practices

### Spatial Hash for Collision Detection
```python
# ALWAYS enable spatial hash for collision-heavy sprite lists
enemies = arcade.SpriteList(use_spatial_hash=True)
projectiles = arcade.SpriteList(use_spatial_hash=True)

# Then collision checks are O(1) instead of O(N²)
hits = arcade.check_for_collision_with_list(player, enemies)
```

### Sound Playback Pattern
```python
# Load once
laser_sound = arcade.Sound(":resources:sounds/laser.wav")

# Play multiple times
player1 = laser_sound.play(volume=0.5)
player2 = laser_sound.play(volume=0.8)

# Check status
if player1.is_playing():
    player1.stop()
```

### Text Performance
```python
# BAD (slow, recalculates every frame)
def on_draw(self):
    arcade.draw_text(f"Score: {self.score}", 10, 10)

# GOOD (fast, update only when needed)
def __init__(self):
    self.score_text = arcade.Text("Score: 0", 10, 10)

def on_draw(self):
    self.score_text.draw()

def add_score(self, points):
    self.score += points
    self.score_text.value = f"Score: {self.score}"
```

### Sprite List Drawing
```python
# Initialize once
self.enemies = arcade.SpriteList(use_spatial_hash=True)

# Add sprites as needed
enemy = arcade.Sprite("enemy.png")
self.enemies.append(enemy)

# Draw all at once (GPU optimized)
def on_draw(self):
    self.enemies.draw()

# Update all
def on_update(self, delta_time):
    self.enemies.update(delta_time)
```

### Resource Loading
```python
# Use resource handles for built-in assets
texture = arcade.load_texture(":resources:images/player.png")
sound = arcade.Sound(":resources:sounds/coin.wav")

# Or use relative/absolute paths
texture = arcade.load_texture("assets/sprites/player.png")
sound = arcade.Sound("assets/audio/explosion.wav")
```

---

## Performance Tips

### Collision Detection Performance

#### Why are collisions slow?

The simplest approach is a for loop over every wall. Even if the hitboxes of both the player and the ground Sprite objects are squares, it will still be a lot of work.

Game developers often use Big O notation to describe:
- The worst-case execution speed of code
- How quickly it grows with the size of the input

In this case, it grows linearly with the number of walls. Therefore, it's called "Order N" or "O(N)" and pronounced "Oh-En".

Adding more moving elements means the number of collision checks will grow very quickly. How do we stop a game from dropping below 60 FPS?

#### The Faster Alternatives

Arcade supports two solutions out the box:

1. The built-in Spatial Hashing
2. The Pymunk physics engine integrations

**Which should I use?**

| Scenario | Recommendation | Use Case |
|----------|----------------|----------|
| Default settings | N < 100 sprites (especially if most move) | Sprites That Follow The Player |
| Spatial hashing | N > 100 mostly non-moving sprites | Line of Sight |
| PymunkPhysicsEngine | You need forces, torque, joints, or springs | Using PyMunk for Physics |

#### Spatial Hashing

Spatial hashing is meant for collision checking sprites against a SpriteList of non-moving sprites:
- Checking collisions against hashed sprites becomes much faster
- Moving or resizing any sprite in the hash becomes much slower

It divides the game world into grid squares of regular size. Then, it uses a hash map (dict) of grid square coordinates to lists of Sprite objects in each square.

**Enabling Spatial Hashing:**
```python
# Inside a Window or View, and often inside a setup() method
self.spritelist_with_hashing = arcade.SpriteList(use_spatial_hash=True)
```

**Spatial Hashing and Tiled Maps:**
```python
layer_options = {
    "ground": {
        "use_spatial_hash": True
    },
    "non_moving_platforms": {
        "use_spatial_hash": True
    }
}
```

**The Catch:**
Spatial hashing doubles the cost of moving or resizing sprites. However, this doesn't mean we can't ever move or resize a sprite! Instead, it means we have to be careful about when and how much we do so.

#### Pymunk Physics Engine

Arcade provides helper wrappers around Pymunk, a binding for the professional-grade Chipmunk2D engine. It offers many features beyond anything Arcade's other built-in physics options currently offer.

None of Arcade's other engines support torque, multiple forces, joints, or springs. If you find yourself needing these or the speed only binary-backed acceleration can offer, this may be the right choice.

### Drawing Performance

To draw at 60 frames per second or better, there are rules you need to follow. The most important is simple: You should draw items the same way you would bake muffins - in batches.

#### Drawing Shapes

The `arcade.draw_*` functions are slow despite being convenient. This is because it does not perform batched drawing. Instead of sending batches of shapes to draw, it sends them individually.

You have three options for drawing shapes more efficiently:
1. Use Arcade's non-modifiable shapes with `arcade.shape_list.ShapeElementList`
2. Use pyglet's updatable `pyglet.shapes` module
3. Write your own advanced shaders

#### Sprite Drawing Performance

Arcade's `arcade.SpriteList` is the only way to draw a Sprite. This is because all drawing with a graphics card is batched drawing. The SpriteList handles batching for you. As a result, you can draw thousands of moving sprites with any extra effort on your part.

**An Option for Advanced Users:**
Advanced users may want to try pyglet's `pyglet.sprite.Sprite`. Instead of Arcade's SpriteList, pyglet sprites use a mix of `pyglet.graphics.Batch` and `pyglet.graphics.Group`.

#### Text Drawing Performance

The slowest thing aside from disk access is `arcade.draw_text()`. To improve performance:
1. Use `arcade.Text` instead
2. (Optional) Pass a pyglet Batch object at creation

### Loading Performance

Disk access is one of the slowest things a computer can do. Your goal for minimizing performance is to reduce the amount of data you read and write during gameplay to a minimum. Fortunately, this is fairly easy. It comes down to one thing above all else: **Preload everything you can before gameplay**.

#### Loading Screens and Rooms

You may be familiar with loading screens. Other approaches include:
- In-game loading "rooms" with minimal performance impact
- Multi-threading to load data on background threads

Both allow background loading of data before gameplay. You can use these for loading audio, textures, and other data before the player enters the game.

### Sound Performance in Depth

#### Static Sounds are for Speed

Static sounds can help your game run smoothly by preloading data before gameplay. Each decompressed minute of CD-quality audio uses slightly over 10 MB of RAM. This adds up quickly.

**When to Use Static Sounds:**
- You need to start playback quickly in response to gameplay
- Two or more "copies" of the sound can be playing at the same time
- You will unpredictably skip to different times in the file
- You will unpredictably restart playback
- You need to automatically loop playback
- The file is a short clip

#### Streaming Saves Memory

Streaming audio from compressed files is similar to streaming video online. Both save memory by transmitting a compressed version over a constrained connection and only decompressing part of a file in memory at a time.

**When to Stream:**
In general, avoid streaming things other than music and ambiance. If you're unsure, avoid streaming unless you can say yes to all of the following:
1. The Sound will have at most one playback at a time
2. The file is long enough to make it worth it
3. Seeking (skipping to different parts) will be infrequent

**Streaming Can Cause Freezes:**
Failing to meet the requirements above can cause buffering issues. Good compression on files can help, but it can't fully overcome it. Each skip outside the currently loaded data requires reading and decompressing a replacement.
