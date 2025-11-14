import pickle
import shlex
from enum import Enum
from functools import wraps
from typing import List, Tuple, Callable, Any, Protocol, TypeVar, Optional, Union, cast
import difflib

from address_book import AddressBook
from notebook import Notebook


class Color(str, Enum):
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    END = "\033[0m"


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

    def __call__(self, args: List[str], target: Optional[Union[AddressBook, Notebook]]) -> str: ...


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
    Load an object from pickle. If missing or corrupted — return a fresh instance.
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
    """
    Load address book from pickle file.
    """
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


def command_desc(command: str, desc: str, usage: Optional[str] = None, example: Optional[str] = None) -> Callable[[Callable[..., str]], Callable[..., str]]:
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
        # Attach attributes for help generation; mypy cannot track arbitrary attributes, but this is fine at runtime.
        setattr(func, "command", command)
        setattr(func, "desc", desc)
        setattr(func, "usage", usage)
        setattr(func, "example", example)
        return func

    return decorator


def suggest_command(command: str, commands: list[str], limit: int = 3) -> list[str]:
    """
    Suggest similar commands using difflib.get_close_matches.
    """
    return difflib.get_close_matches(command, commands, n=limit, cutoff=0.45)


def print_help(command: str, usage: str, description: str, example: Optional[str] = None) -> str:
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
