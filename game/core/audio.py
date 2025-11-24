import math
import struct
import time
import wave
from pathlib import Path

import arcade


class SoundManager:
    def __init__(self, base_path: Path, volume_config: dict | None = None, cooldowns: dict | None = None):
        self.base_path = Path(base_path)
        self.sounds: dict[str, arcade.Sound] = {}
        self.last_play_times: dict[str, float] = {}
        self.volume_config = {
            "master": 0.5,
            "sfx": {
                "attack": 0.25,
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
                self.sounds[key] = arcade.load_sound(path)

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

    def play(self, name: str):
        sound = self.sounds.get(name)
        if not sound:
            return

        now = time.time()
        last_played = self.last_play_times.get(name, 0.0)
        min_interval = self.cooldowns.get(name, self.cooldowns.get("default", 0.0))

        if now - last_played < min_interval:
            return

        volume = self.volume_config.get("master", 1.0) * self.volume_config.get("sfx", {}).get(name, 1.0)
        arcade.play_sound(sound, volume=volume)
        self.last_play_times[name] = now
