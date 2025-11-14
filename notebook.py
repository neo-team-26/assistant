import os
import re
from typing import List, Optional, Tuple, Pattern, Set

from collections import UserDict


def _get_sort_key(item: Tuple[str, 'NoteEntry']) -> str:
    """Defines the sorting key: the first tag or the note name."""
    name, note_entry = item
    tags = note_entry.tags
    if tags:
        # Sort by the first tag
        return tags[0]
    # Notes without tags go last, sorted by name
    return "~" + name


class NoteEntry:
    """Class to hold the content and tags of a single note."""
    def __init__(self, text: str, tags: Optional[List[str]] = None):
        self._text = text
        self._tags: Set[str] = set(self._normalize_tags(tags or []))

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, new_text: str) -> None:
        self._text = new_text

    @property
    def tags(self) -> List[str]:
        # Return tags as a sorted list for consistency
        return sorted(list(self._tags))

    def _normalize_tags(self, tags: List[str]) -> List[str]:
        """Convert tags to lowercase for case-insensitive storage/search."""
        return [tag.lower() for tag in tags if tag.strip()]

    def add_tags(self, new_tags: List[str]) -> None:
        self._tags.update(self._normalize_tags(new_tags))

    def remove_tag(self, tag: str) -> bool:
        """Removes a tag. Returns True if removed, False otherwise."""
        normalized_tag = tag.lower()
        if normalized_tag in self._tags:
            self._tags.remove(normalized_tag)
            return True
        return False

    def __str__(self) -> str:
        tag_str = f" #{' #'.join(self.tags)}" if self.tags else ""
        return f"{self.text}{tag_str}"

    def get_searchable_content(self) -> str:
        """Returns content for case-insensitive text search (text + tags)."""
        return f"{self.text} {' '.join(self.tags)}"


class Notebook(UserDict[str, NoteEntry]): # Value type changed to NoteEntry
    """Class for storing and managing Notes. Inherits from UserDict.

    Keys are strings (note name), values are NoteEntry objects.
    """

    def add_note(self, name: str, note_text: str, tags: Optional[List[str]] = None) -> None:
        if name in self.data:
            raise ValueError(
                f"Notebook already contains '{name}' note. please use 'edit-note' command or provide a different name"
            )

        self.data[name] = NoteEntry(note_text, tags)

    def edit_note(self, name: str, text: str) -> None:
        note_entry = self.data.get(name)
        if note_entry:
            note_entry.text = text
        else:
            raise KeyError(f"Note '{name}' not found.")

    def add_tags_to_note(self, name: str, tags: List[str]) -> None:
        note_entry = self.data.get(name)
        if note_entry:
            note_entry.add_tags(tags)
        else:
            raise KeyError(f"Note '{name}' not found.")

    def remove_tag_from_note(self, name: str, tag: str) -> None:
        note_entry = self.data.get(name)
        if note_entry:
            if not note_entry.remove_tag(tag):
                raise ValueError(f"Tag '{tag}' not found in note '{name}'.")
        else:
            raise KeyError(f"Note '{name}' not found.")

    def delete_note(self, name: str) -> None:
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError("Note was not found")

    def list_notes(self) -> str:
        """
        Return a newline-separated listing of notes in the form 'name: text #tag1 #tag2'.
        Notes are sorted by their first tag.
        """
        items = list(self.data.items())

        items.sort(key=_get_sort_key)

        result: List[str] = []
        for name, note_entry in items:
            result.append(f"{name}: {note_entry}") # Using NoteEntry's __str__
        return os.linesep.join(result)

    def get_note(self, name: str) -> Optional[str]:
        """Get the full string representation of a note by its name. Returns None if not found."""
        note_entry = self.data.get(name)
        return str(note_entry) if note_entry else None

    def find_notes(
            self,
            and_words: List[str],
            or_words: List[str],
            not_words: List[str],
            required_tags: List[str]
    ) -> List[Tuple[str, str]]:
        """
        Find notes that match ALL provided criteria (text AND tags).

        Text criteria (if provided):
        1. All 'AND' words (must be present).
        2. At least one 'OR' word (if OR words provided, one must match).
        3. No 'NOT' words (must be absent).

        Tag criteria (if provided):
        4. At least one 'required_tag' (OR logic for tags).

        Results are always sorted by the first tag.
        """
        has_text_search = and_words or or_words or not_words
        has_tag_search = required_tags

        if not has_text_search and not has_tag_search:
            return []

        matching_notes: List[Tuple[str, NoteEntry]] = []

        # 1. Prepare patterns for text search
        and_patterns: List[Pattern[str]] = []
        if and_words:
            and_patterns = [re.compile(re.escape(w), re.IGNORECASE) for w in and_words]

        or_pattern: Optional[Pattern[str]] = None
        if or_words:
            pattern_str = "|".join([re.escape(w) for w in or_words if w])
            if pattern_str:
                or_pattern = re.compile(pattern_str, re.IGNORECASE)

        not_pattern: Optional[Pattern[str]] = None
        if not_words:
            pattern_str = "|".join([re.escape(w) for w in not_words if w])
            if pattern_str:
                not_pattern = re.compile(pattern_str, re.IGNORECASE)

        # 2. Prepare for tag filtering (OR logic)
        normalized_tags: Set[str] = set([tag.lower() for tag in required_tags])

        for name, note_entry in self.data.items():
            search_content = note_entry.get_searchable_content()

            # Text Filtering (Step 1: NOT)
            if not_pattern and (not_pattern.search(search_content) or not_pattern.search(name)):
                continue # Exclude the note

            # Text Filtering (Step 2: AND)
            and_match = all(p.search(search_content) or p.search(name) for p in and_patterns)

            # Text Filtering (Step 3: OR)
            or_match = True
            if or_words: # Only if OR words were provided
                or_match = bool(or_pattern and (or_pattern.search(search_content) or or_pattern.search(name)))

            # Final text match (AND and OR)
            text_match = and_match and or_match

            # If no text search criteria were set, assume a match
            if not has_text_search:
                text_match = True


            # Tag Filtering (Step 4: OR)
            tag_match = False
            if normalized_tags:
                tag_match = bool(normalized_tags.intersection(note_entry._tags))

            # If no tag search criteria were set, assume a match
            if not has_tag_search:
                tag_match = True


            # Note inclusion: must match the text part AND the tag part
            if text_match and tag_match:
                matching_notes.append((name, note_entry))

        matching_notes.sort(key=_get_sort_key)

        return [(name, str(note_entry)) for name, note_entry in matching_notes]
