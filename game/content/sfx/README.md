# Sound placeholders

This directory is kept in version control without bundling binary assets. During
runtime, `SoundManager.load_sounds` generates tiny synthesized WAV placeholders
for each expected cue if no file is present. Replace them with real SFX by
dropping files with the same names (e.g., `attack.wav`, `hit.wav`).
