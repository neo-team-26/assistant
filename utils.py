import pickle
import shlex
from enum import Enum
from functools import wraps
from typing import (List, Tuple, Callable, Any, Protocol,
                    TypeVar, Optional, Union, cast)
import difflib
import textwrap

from address_book import AddressBook
from notebook import Notebook


class Color(str, Enum):
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    END = "\033[0m"
    BOLD = "\033[1m"


ADDRESSBOOK_FILE = "addressbook.pkl"
NOTEBOOK_FILE = "notebook.pkl"

# Generic type for pickle loader
U = TypeVar("U")


class Handler(Protocol):
    """
    Protocol for all command handlers.

    The handler receives a list of string args and an optional target object
    (either an AddressBook or a Notebook) and returns a string message.
    """

    def __call__(
        self, args: List[str], target: Optional[Union[AddressBook, Notebook]]
    ) -> str: ...


def colored_message(message: str, color: Color) -> str:
    """Wrap message in ANSI color codes."""
    return f"{color.value}{message}{Color.END.value}"


def parse_input(user_input: str) -> Tuple[str, List[str]]:
    """
    Parse command and arguments using shlex for robust quoting support.
    """
    user_input = user_input.strip()
    if not user_input:
        return "", []

    parts = shlex.split(user_input)
    command = parts[0].lower()
    args = parts[1:]
    return command, args


def input_error(func: Callable[..., str]) -> Callable[..., str]:
    """
    Decorator for safe command execution with nice error messages.
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> str:
        try:
            return func(*args, **kwargs)
        except (ValueError, IndexError, KeyError) as e:
            return colored_message(str(e), Color.RED)

    return wrapper


def load_pickle(filename: str, factory: Callable[[], U]) -> U:
    """
    Load an object from pickle.
    If missing or corrupted — return a fresh instance.
    """
    try:
        with open(filename, "rb") as f:
            # cast the result of pickle.load to the expected type
            return cast(U, pickle.load(f))
    except FileNotFoundError:
        print(f"File '{filename}' not found. Creating a new instance.")
        return factory()
    except Exception as e:
        print(colored_message(
            f"Error loading '{filename}': {e}. Creating new instance.",
            Color.RED
        ))
        return factory()


def load_addressbook(filename: str = ADDRESSBOOK_FILE) -> AddressBook:
    return load_pickle(filename, AddressBook)


def load_notes(filename: str = NOTEBOOK_FILE) -> Notebook:
    """
    Load notebook from pickle file.
    """
    return load_pickle(filename, Notebook)


def save_data(data: Any, filename: str) -> None:
    """
    Save any pickle-serializable object to the given file.
    """
    try:
        with open(filename, "wb") as f:
            pickle.dump(data, cast(Any, f))
        print(colored_message(f"Data saved to '{filename}'.", Color.GREEN))
    except Exception as e:
        print(colored_message(f"Error saving '{filename}': {e}", Color.RED))
        raise


def save_all(book: AddressBook, notes: Notebook) -> None:
    """
    Save all application data (address book + notebook) in one call.
    """
    save_data(book, ADDRESSBOOK_FILE)
    save_data(notes, NOTEBOOK_FILE)


def command_desc(
    command: str, desc: str,
    usage: Optional[str] = None, example: Optional[str] = None
) -> Callable[[Callable[..., str]], Callable[..., str]]:
    """
    Decorator to add metadata to a command handler.

    Args:
        command: The string command name.
        desc: Short description of the command.
        usage: Optional usage instructions.
        example: Optional example of command usage.

    Returns:
        Callable: The same function with metadata attributes added.
    """
    def decorator(func: Callable[..., str]) -> Callable[..., str]:
        # Attach attributes for help generation; mypy cannot track arbitrary
        # attributes, but this is fine at runtime.
        setattr(func, "command", command)
        setattr(func, "desc", desc)
        setattr(func, "usage", usage)
        setattr(func, "example", example)
        return func

    return decorator


def suggest_command(command: str,
                    commands: list[str],
                    limit: int = 5) -> list[str]:
    """
    Suggest similar commands using difflib.get_close_matches.
    """
    return difflib.get_close_matches(command,
                                     commands,
                                     n=limit, cutoff=0.45)


def print_help(command: str, usage: str,
               description: str,
               example: Optional[str] = None) -> str:
    """
    Return a nicely formatted help text for a command.
    """
    line = "─" * 50
    out = [
        colored_message(line, Color.CYAN),
        colored_message(f"  HELP: {command}", Color.CYAN),
        colored_message(line, Color.CYAN),
        "",
        colored_message("USAGE:", Color.YELLOW),
        f"  {usage}\n",
        colored_message("DESCRIPTION:", Color.YELLOW),
        f"  {description}\n"
    ]

    if example:
        out.append(colored_message("EXAMPLE:", Color.YELLOW))
        out.append(f"  {example}\n")

    return "\n".join(out)


def tab_output(
    data, headers, max_col_width: int = 30,
    custom_widths: Optional[List[int]] = None
):
    """
    Format a table where cells may contain multiple values.
    Returns a string suitable for console output.
    """

    # Normalize rows: every cell -> list of item-strings
    # (one item per logical subline)
    normalized_rows = []
    for row in data:
        norm_row = []
        for cell in row:
            if cell is None:
                norm_row.append([""])
            elif isinstance(cell, (list, tuple)):
                norm_row.append([str(x) for x in cell] if cell else [""])
            else:
                norm_row.append([str(cell)])
        normalized_rows.append(norm_row)

    # Determine maximum length per column across all items (before wrapping)
    num_cols = len(headers)
    max_lens = [len(headers[i]) for i in range(num_cols)]
    for norm_row in normalized_rows:
        for col in range(num_cols):
            if col < len(norm_row):
                for item in norm_row[col]:
                    max_lens[col] = max(max_lens[col], len(str(item)))

    # Compute final widths: use custom_widths if provided
    # else clamp by max_col_width
    widths: List[int] = [0] * num_cols
    for i in range(num_cols):
        if custom_widths and i < len(custom_widths) and custom_widths[i]:
            widths[i] = max(len(headers[i]), custom_widths[i])
        else:
            widths[i] = max(len(headers[i]), min(max_col_width, max_lens[i]))

    # Now wrap each cell's items according to computed widths
    # so each item may produce multiple lines
    wrapped_rows = []
    for norm_row in normalized_rows:
        wrapped_row = []
        for col in range(num_cols):
            if col < len(norm_row):
                items = norm_row[col]
                cell_lines = []
                for it in items:
                    if not it:
                        cell_lines.append("")
                    else:
                        wrapped = textwrap.wrap(it, width=widths[col])
                        if not wrapped:
                            cell_lines.append("")
                        else:
                            cell_lines.extend(wrapped)
                wrapped_row.append(cell_lines)
            else:
                wrapped_row.append([""])
        wrapped_rows.append(wrapped_row)

    # For each record, compute how many sublines are needed after wrapping
    row_sublines = [
        max(len(cell_lines) for cell_lines in wrapped_row)
        for wrapped_row in wrapped_rows
    ]

    # Ensure Name (col 0) and ID (col 1) are shown only on the first subline
    for idx, wrapped_row in enumerate(wrapped_rows):
        if len(wrapped_row) >= 2:
            for j in range(1, row_sublines[idx]):
                if len(wrapped_row[0]) < row_sublines[idx]:
                    wrapped_row[0] += [""] * (
                        row_sublines[idx] - len(wrapped_row[0])
                    )
                if len(wrapped_row[1]) < row_sublines[idx]:
                    wrapped_row[1] += [""] * (
                        row_sublines[idx] - len(wrapped_row[1])
                    )
                wrapped_row[0][j] = ""
                wrapped_row[1][j] = ""

    # Build separator line and header (bold, centered)
    sep = '+'
    for w in widths:
        sep += '-' * (w + 2) + '+'

    header_cells = []
    for i, h in enumerate(headers):
        header_cells.append(f" {h:^{widths[i]}} ")
    header = '|' + '|'.join(header_cells) + '|'
    header = Color.BOLD.value + header + Color.END.value

    lines = [sep, header, sep]

    for wrapped_row, nlines in zip(wrapped_rows, row_sublines):
        for line_idx in range(nlines):
            cells = []
            for col in range(num_cols):
                cell_lines = (
                    wrapped_row[col] if col < len(wrapped_row) else [""]
                )
                if line_idx < len(cell_lines):
                    val = cell_lines[line_idx]
                else:
                    val = ""
                cells.append(f" {val:<{widths[col]}} ")
            row_line = '|' + '|'.join(cells) + '|'
            lines.append(row_line)
        lines.append(sep)

    return '\n'.join(lines)
