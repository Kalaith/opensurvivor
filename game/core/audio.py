import math
import struct
import time
import wave
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path

import arcade
from arcade.sound import Sound


class SoundPriority(IntEnum):
    """Priority levels for sound playback."""
    CRITICAL = 5    # Player death, level up, game-changing events
    HIGH = 4        # Player damage, boss attacks, important pickups
    MEDIUM = 3      # Enemy hits, weapon attacks, XP collection
    LOW = 2         # Ambient sounds, minor enemy hits
    BACKGROUND = 1  # Environmental sounds, music


@dataclass
class PlayingSound:
    """Metadata for a currently playing sound."""
    player: object  # pyglet Player instance from sound.play()
    name: str
    priority: int
    start_time: float
    source_position: tuple[float, float] | None = None
    channel: str = "default"


class SoundManager:
    def __init__(self, base_path: Path, volume_config: dict | None = None, cooldowns: dict | None = None):
        self.base_path = Path(base_path)
        self.sounds: dict[str, arcade.Sound] = {}
        self.last_play_times: dict[str, float] = {}
        self.volume_config = {
            "master": 0.5,
            "sfx": {
                "attack": 0.1,
                "hit": 0.35,
                "xp_collect": 0.25,
                "level_up": 0.5,
            },
        }
        if volume_config:
            # Shallow merge for simple configuration
            self.volume_config["master"] = volume_config.get("master", self.volume_config["master"])
            self.volume_config["sfx"].update(volume_config.get("sfx", {}))

        default_cooldowns = {
            "default": 0.05,
            "attack": 0.1,
            "hit": 0.08,
            "xp_collect": 0.02,
            "level_up": 0.5,
        }
        self.cooldowns = {**default_cooldowns, **(cooldowns or {})}

        # Priority-based channel system
        self.channel_groups = {
            "combat": {
                "max_concurrent": 8,
                "sounds": ["hit", "attack"],
                "priority_boost": 0,
            },
            "player_feedback": {
                "max_concurrent": 4,
                "sounds": ["level_up", "xp_collect"],
                "priority_boost": 1,  # +1 priority for player-related sounds
            },
        }

        # Sound configuration with priorities
        self.sound_config = {
            "hit": {
                "priority": SoundPriority.MEDIUM,
                "channel": "combat",
                "interrupt_lower": True,
            },
            "attack": {
                "priority": SoundPriority.MEDIUM,
                "channel": "combat",
                "interrupt_lower": False,
            },
            "level_up": {
                "priority": SoundPriority.CRITICAL,
                "channel": "player_feedback",
                "interrupt_lower": True,
            },
            "xp_collect": {
                "priority": SoundPriority.MEDIUM,
                "channel": "player_feedback",
                "interrupt_lower": False,
            },
        }

        # Active sounds organized by channel (priority-based)
        self.active_sounds_by_channel: dict[str, list[PlayingSound]] = {
            channel: [] for channel in self.channel_groups.keys()
        }

    def load_sounds(self):
        sound_files = {
            "attack": ("attack.wav", 640),
            "hit": ("hit.wav", 420),
            "xp_collect": ("xp_collect.wav", 520),
            "level_up": ("level_up.wav", 760),
        }

        self._ensure_sound_assets(sound_files)

        for key, filename in ((k, v[0]) for k, v in sound_files.items()):
            path = self.base_path / filename
            if path.exists():
                self.sounds[key] = arcade.Sound(path)

    def _ensure_sound_assets(self, sound_files: dict[str, tuple[str, int]]):
        """Generate tiny placeholder WAVs if the assets are missing."""

        self.base_path.mkdir(parents=True, exist_ok=True)

        for _, (filename, frequency) in sound_files.items():
            path = self.base_path / filename
            if path.exists():
                continue
            self._write_placeholder_wave(path, frequency)

    def _write_placeholder_wave(self, path: Path, frequency: int, duration: float = 0.25):
        sample_rate = 44100
        amplitude = 8000
        num_frames = int(sample_rate * duration)

        # `wave.open` only accepts string paths or file objects; providing a
        # `Path` directly leaves the underlying `Wave_write` object holding a
        # `Path` instead of an open file handle, which causes an AttributeError
        # when it tries to write the header on Windows. Convert to `str` to
        # ensure the file is opened correctly on all platforms.
        with wave.open(str(path), "w") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)  # 16-bit samples
            wav_file.setframerate(sample_rate)

            for i in range(num_frames):
                sample = int(amplitude * math.sin(2 * math.pi * frequency * i / sample_rate))
                wav_file.writeframes(struct.pack("<h", sample))

    def play(
        self, 
        name: str, 
        position: tuple[float, float] | None = None,
        priority_override: int | None = None,
        force: bool = False
    ) -> bool:
        """
        Play a sound with priority and spatial audio support.
        
        Args:
            name: Sound identifier
            position: World position for spatial audio (x, y)
            priority_override: Override default priority
            force: Force play even if at channel limit
        
        Returns:
            True if sound played, False if rejected
        """
        sound = self.sounds.get(name)
        if not sound:
            return False

        # Check cooldown
        now = time.time()
        last_played = self.last_play_times.get(name, 0.0)
        min_interval = self.cooldowns.get(name, self.cooldowns.get("default", 0.0))

        if not force and now - last_played < min_interval:
            return False

        # Get sound configuration
        config = self.sound_config.get(name, {})
        channel_name = config.get("channel", "combat")
        priority = priority_override if priority_override is not None else config.get("priority", SoundPriority.MEDIUM)
        
        # Apply channel priority boost
        channel_config = self.channel_groups.get(channel_name, {})
        priority += channel_config.get("priority_boost", 0)

        # Check if we can play this sound
        if not force and not self._can_play_sound(channel_name, priority, config.get("interrupt_lower", False)):
            return False

        # Calculate volume
        volume = self.volume_config.get("master", 1.0) * self.volume_config.get("sfx", {}).get(name, 1.0)
        
        # Play the sound (returns a player object that we can check status on)
        played_sound = sound.play(volume=volume)
        
        # Track the playing sound
        playing_sound = PlayingSound(
            player=played_sound,
            name=name,
            priority=priority,
            start_time=now,
            source_position=position,
            channel=channel_name
        )
        
        self.active_sounds_by_channel[channel_name].append(playing_sound)
        self.last_play_times[name] = now
        
        return True

    def _can_play_sound(self, channel: str, priority: int, can_interrupt: bool) -> bool:
        """
        Determine if a sound can be played based on channel capacity and priority.
        
        Args:
            channel: Channel name
            priority: Priority of the sound to play
            can_interrupt: Whether this sound can interrupt lower priority sounds
        
        Returns:
            True if sound can play, False otherwise
        """
        # Cleanup finished sounds first
        self._cleanup_finished_sounds_in_channel(channel)
        
        channel_config = self.channel_groups.get(channel, {})
        max_concurrent = channel_config.get("max_concurrent", 4)
        active_sounds = self.active_sounds_by_channel.get(channel, [])
        
        # If channel has capacity, allow
        if len(active_sounds) < max_concurrent:
            return True
        
        # If we can interrupt, check if there's a lower priority sound
        if can_interrupt:
            # Find lowest priority sound
            lowest_priority_sound = min(active_sounds, key=lambda s: s.priority)
            if lowest_priority_sound.priority < priority:
                # Stop the lowest priority sound to make room
                lowest_priority_sound.player.stop()
                active_sounds.remove(lowest_priority_sound)
                return True
        
        return False

    def _cleanup_finished_sounds_in_channel(self, channel: str):
        """Remove finished sounds from a specific channel."""
        if channel not in self.active_sounds_by_channel:
            return
        
        self.active_sounds_by_channel[channel] = [
            playing_sound for playing_sound in self.active_sounds_by_channel[channel]
            if getattr(playing_sound.player, '_playing', False)
        ]

    def get_channel_stats(self) -> dict:
        """Get current state of all channels for debugging."""
        stats = {}
        for channel_name, playing_sounds in self.active_sounds_by_channel.items():
            self._cleanup_finished_sounds_in_channel(channel_name)
            channel_config = self.channel_groups.get(channel_name, {})
            stats[channel_name] = {
                "active": len(playing_sounds),
                "max": channel_config.get("max_concurrent", 0),
                "sounds": [
                    {
                        "name": ps.name,
                        "priority": ps.priority,
                        "age": time.time() - ps.start_time
                    }
                    for ps in playing_sounds
                ]
            }
        return stats
