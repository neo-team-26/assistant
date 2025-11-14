import os
import re

from collections import UserDict


class Notebook(UserDict):
    """Class for storing and managing Notes. Inherits from UserDict."""

    def add_note(self, name: str, note: str) -> None:
        if name in self.data.keys():
            raise ValueError(f"Notebook contains {name} note. please use edit_note command or provide different name")

        self.data[name] = note

    def edit_note(self, name: str, text: str) -> None:
        note = self.data.get(name)
        if note:
            self.data[name] = text

    def delete_note(self, name: str) -> None:
        if name in self.data.keys():
            del self.data[name]
        else:
            raise ValueError("Note was not found")

    def list_notes(self):
        result = []
        for name, text in self.data.items():
            result.append(f"{name}: {text}")
        return os.linesep.join(result)

    def get_note(self, name: str) -> str:
        return self.data.get(name)

    def find_notes(self, *args: str) -> list[(str, str)]:
        notes = []
        search_words = list(args)[0][0]
        search_template = r""
        for key in search_words:
            search_template = search_template + key + "|"
        search_template = search_template[:-1]
        search_template = re.compile(search_template, re.IGNORECASE)

        for key, value in self.data.items():
            if re.search(search_template, value):
                notes.append((key, value))
        return notes
