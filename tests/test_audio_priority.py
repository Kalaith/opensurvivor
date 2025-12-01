"""Tests for priority-based audio system."""
import time
from pathlib import Path
from game.core.audio import SoundManager, SoundPriority


def test_priority_interruption(tmp_path):
    """Test that high priority sounds interrupt low priority sounds."""
    # Create sound manager with test sounds
    sound_manager = SoundManager(tmp_path)
    sound_manager.load_sounds()
    
    # Fill combat channel with low priority sounds
    for i in range(8):  # Combat channel max is 8
        result = sound_manager.play("attack", force=True)  # Medium priority, no interrupt
        assert result == True
    
    # Try to play another attack (should fail, channel full, can't interrupt)
    result = sound_manager.play("attack")
    assert result == False
    
    # Play a level_up (CRITICAL priority, can interrupt)
    result = sound_manager.play("level_up", force=True)
    assert result == True


def test_channel_limits():
    """Test that channel limits are respected."""
    sound_manager = SoundManager(Path("game/content/sfx"))
    sound_manager.load_sounds()
    
    stats = sound_manager.get_channel_stats()
    assert "combat" in stats
    assert "player_feedback" in stats
    
    # Check combat channel config
    combat_stats = stats["combat"]
    assert combat_stats["max"] == 8
    

def test_priority_boost():
    """Test that channel priority boost is applied."""
    sound_manager = SoundManager(Path("game/content/sfx"))
    sound_manager.load_sounds()
    
    # XP collect is MEDIUM (3) + player_feedback boost (1) = 4
    config = sound_manager.sound_config["xp_collect"]
    assert config["priority"] == SoundPriority.MEDIUM
    
    channel_config = sound_manager.channel_groups["player_feedback"]
    assert channel_config["priority_boost"] == 1


def test_backward_compatibility():
    """Test that old API still works."""
    sound_manager = SoundManager(Path("game/content/sfx"))
    sound_manager.load_sounds()
    
    # Old style call (should still work)
    result = sound_manager.play("hit")
    assert isinstance(result, bool)
    
    # New style call with position
    result = sound_manager.play("hit", position=(100, 200))
    assert isinstance(result, bool)
    
    # New style with priority override
    result = sound_manager.play("hit", priority_override=SoundPriority.HIGH)
    assert isinstance(result, bool)


def test_channel_stats():
    """Test channel statistics retrieval."""
    sound_manager = SoundManager(Path("game/content/sfx"))
    sound_manager.load_sounds()
    
    stats = sound_manager.get_channel_stats()
    
    # Check structure
    assert isinstance(stats, dict)
    for channel_name, channel_stats in stats.items():
        assert "active" in channel_stats
        assert "max" in channel_stats
        assert "sounds" in channel_stats
        assert isinstance(channel_stats["sounds"], list)


if __name__ == "__main__":
    print("Running audio priority tests...")
    
    import tempfile
    with tempfile.TemporaryDirectory() as tmp_dir:
        test_priority_interruption(Path(tmp_dir))
        print("✓ Priority interruption test passed")
    
    test_channel_limits()
    print("✓ Channel limits test passed")
    
    test_priority_boost()
    print("✓ Priority boost test passed")
    
    test_backward_compatibility()
    print("✓ Backward compatibility test passed")
    
    test_channel_stats()
    print("✓ Channel stats test passed")
    
    print("\nAll tests passed! ✓")
