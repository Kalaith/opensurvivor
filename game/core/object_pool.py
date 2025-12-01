from typing import Type, TypeVar, Generic, List, Callable, Any
import arcade

T = TypeVar('T')

class ObjectPool(Generic[T]):
    """Generic object pool to reduce allocations by reusing objects."""

    def __init__(self, object_class: Type[T], initial_size: int = 10, max_size: int = 1000):
        self.object_class = object_class
        self.max_size = max_size
        self.available: List[T] = []
        self.in_use: List[T] = []

        # Pre-populate the pool
        for _ in range(initial_size):
            obj = object_class.__new__(object_class)
            self.available.append(obj)

    def get(self, *args, **kwargs) -> T:
        """Get an object from the pool, creating a new one if necessary."""
        if self.available:
            obj = self.available.pop()
            # Reinitialize the object
            if hasattr(obj, '__init__'):
                obj.__init__(*args, **kwargs)
        else:
            # Create new object if pool is empty
            obj = self.object_class(*args, **kwargs)

        self.in_use.append(obj)
        return obj

    def release(self, obj: T) -> None:
        """Return an object to the pool for reuse."""
        if obj in self.in_use:
            self.in_use.remove(obj)

            # Reset object state if it has a reset method
            if hasattr(obj, 'reset'):
                obj.reset()

            # Only keep in pool if under max size
            if len(self.available) < self.max_size:
                self.available.append(obj)

    def release_all(self) -> None:
        """Release all objects back to the pool."""
        for obj in self.in_use[:]:  # Copy the list to avoid modification during iteration
            self.release(obj)

    def get_stats(self) -> dict:
        """Get pool statistics for monitoring."""
        return {
            'available': len(self.available),
            'in_use': len(self.in_use),
            'total': len(self.available) + len(self.in_use)
        }


class SpriteObjectPool(ObjectPool[arcade.Sprite]):
    """Specialized pool for Arcade sprites that handles sprite list management."""

    def __init__(self, object_class: Type[arcade.Sprite], initial_size: int = 10, max_size: int = 1000):
        super().__init__(object_class, initial_size, max_size)

    def get_and_add_to_lists(self, sprite_lists: List[arcade.SpriteList], *args, **kwargs) -> arcade.Sprite:
        """Get an object and automatically add it to the specified sprite lists."""
        obj = self.get(*args, **kwargs)
        for sprite_list in sprite_lists:
            sprite_list.append(obj)
        return obj

    def release_and_remove_from_lists(self, obj: arcade.Sprite, sprite_lists: List[arcade.SpriteList]) -> None:
        """Release an object and remove it from the specified sprite lists."""
        for sprite_list in sprite_lists:
            if obj in sprite_list:
                sprite_list.remove(obj)
        self.release(obj)