import os
import re
from typing import List, Optional, Tuple, Pattern

from collections import UserDict


class Notebook(UserDict[str, str]):
    """Class for storing and managing Notes. Inherits from UserDict.

    Keys and values are both strings: note name -> note text.
    """

    def add_note(self, name: str, note: str) -> None:
        if name in self.data:
            raise ValueError(
                f"Notebook already contains '{name}' note. please use 'edit-note' command or provide a different name"
            )

        self.data[name] = note

    def edit_note(self, name: str, text: str) -> None:
        if name in self.data:
            self.data[name] = text

    def delete_note(self, name: str) -> None:
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError("Note was not found")

    def list_notes(self) -> str:
        """Return a newline-separated listing of notes in the form 'name: text'."""
        result: List[str] = []
        for name, text in self.data.items():
            result.append(f"{name}: {text}")
        return os.linesep.join(result)

    def get_note(self, name: str) -> Optional[str]:
        """Get the text of a note by its name. Returns None if not found."""
        return self.data.get(name)

    def find_notes(self, *search_words: str) -> List[Tuple[str, str]]:
        """Find notes whose text (or name) matches any of the provided search words.

        Usage: find_notes('alice', 'todo')
        Returns a list of (name, text) tuples where any search word appears (case-insensitive).
        """
        if not search_words:
            return []

        escaped_terms = [re.escape(w) for w in search_words if w]
        if not escaped_terms:
            return []

        pattern_str = "|".join(escaped_terms)
        pattern: Pattern[str] = re.compile(pattern_str, re.IGNORECASE)

        notes: List[Tuple[str, str]] = []
        for key, value in self.data.items():
            # Search both the note name and the note text for matches
            if pattern.search(value) or pattern.search(key):
                notes.append((key, value))
        return notes
