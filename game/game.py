"""game.py

Core module for the Python game project based on the Game Design Document (GDD).

This skeleton provides:
- `Game` class that loads the GDD markdown file.
- Simple parsing to extract sections (e.g., "Gameplay", "Story", "Mechanics").
- `run` method placeholder where the main game loop would be implemented.

The implementation is intentionally minimal – the goal is to give you a solid starting point
that you can extend with actual game logic, assets, and UI.
"""

import pathlib
import re
from typing import Dict, List

class Game:
    """Represent the game defined by the GDD.

    Attributes
    ----------
    gdd_path: pathlib.Path
        Path to the GDD markdown file.
    sections: Dict[str, str]
        Mapping of section titles to their markdown content.
    """

    SECTION_HEADER_RE = re.compile(r"^#\s+(.*)$", re.MULTILINE)

    def __init__(self, gdd_path: pathlib.Path | str | None = None):
        # Resolve the path to the GDD.md located two levels up from this file
        if gdd_path is None:
            self.gdd_path = pathlib.Path(__file__).resolve().parents[2] / "GDD.md"
        else:
            self.gdd_path = pathlib.Path(gdd_path).expanduser().resolve()
        self.sections: Dict[str, str] = {}
        self._load_gdd()

    def _load_gdd(self) -> None:
        """Read the GDD file and populate ``self.sections``.

        The parser looks for top‑level markdown headings (single ``#``) and stores the
        content that follows each heading until the next heading.
        """
        if not self.gdd_path.is_file():
            raise FileNotFoundError(f"GDD file not found at {self.gdd_path}")
        raw = self.gdd_path.read_text(encoding="utf-8")
        # Find all headings and their start positions
        headings = [(m.group(1).strip(), m.start()) for m in self.SECTION_HEADER_RE.finditer(raw)]
        for idx, (title, start) in enumerate(headings):
            end = headings[idx + 1][1] if idx + 1 < len(headings) else len(raw)
            content = raw[start:end].strip()
            self.sections[title] = content

    def get_section(self, title: str) -> str | None:
        """Return the markdown for a given section title, or ``None`` if missing."""
        return self.sections.get(title)

    def list_sections(self) -> List[str]:
        """Return a list of all section titles found in the GDD."""
        return list(self.sections.keys())

    def run(self) -> None:
        """Placeholder for the main game loop.

        In a real implementation you would initialise your engine, load assets, and
        start the interactive loop here. For now we simply print the available
        sections to demonstrate that the GDD was parsed correctly.
        """
        print("--- Game Design Document Sections ---")
        for title in self.list_sections():
            print(f"* {title}")
        print("\nGame loop would start here…")

if __name__ == "__main__":
    game = Game()
    game.run()
