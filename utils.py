import pickle
from functools import wraps
from typing import List, Optional, Literal, Tuple, Callable, Any
import difflib

# --- Constants ---
from address_book import AddressBook

RED_COLOR = "\033[91m"
GREEN_COLOR = "\033[92m"
END_COLOR = "\033[0m"
CYAN_COLOR = "\033[96m"
YELLOW_COLOR = "\033[93m"

FILENAME = "addressbook.pkl"



def colored_message(message: str, color: str) -> str:
    """
    Cover the message in ANSI escape sequences for colored output.
    """
    return f"{color}{message}{END_COLOR}"


def parse_input(user_input: str) -> Tuple[str, List[str]]:
    """
    Parses the user input string into a command and a list of arguments,
    supporting arguments enclosed in quotes.
    """
    args: List[str] = []
    current_arg: str = ""
    in_quotes: Optional[Literal] = None
    user_input = ' '.join(user_input.split())
    if not user_input:
        return "", []
    parts = user_input.split(maxsplit=1)
    command = parts[0].strip().lower()
    if len(parts) == 1:
        return command, []
    args_string = parts[1]
    for char in args_string:
        if in_quotes is not None:
            if char == in_quotes:
                in_quotes = None
            else:
                current_arg += char
        else:
            if char in ('"', "'"):
                in_quotes = char
            elif char == ' ':
                if current_arg:
                    args.append(current_arg)
                current_arg = ""
            else:
                current_arg += char
    # Handle the last argument
    if current_arg or (current_arg == "" and in_quotes is None and args_string.endswith(('"', "'")) and not args):
        args.append(current_arg)

    # Remove empty strings resulting from quote handling cleanup
    args = [arg for arg in args if arg]

    return command, args


def input_error(func: Callable[..., str]) -> Callable[..., str]:
    """
    A decorator that handles KeyError, ValueError, and IndexError exceptions
    raised in command handler functions and returns the error message in RED.
    """

    @wraps(func)
    def inner(*args: Any, **kwargs: Any) -> str:
        try:
            return func(*args, **kwargs)
        except (ValueError, IndexError, KeyError) as e:
            return colored_message(str(e), RED_COLOR)

    return inner


def load_data(filename: str = FILENAME) -> 'AddressBook':
    """
    Loads the AddressBook object from a file using pickle.
    Returns a new AddressBook if the file is not found or corrupted.
    """
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        print(f"File '{filename}' not found. Creating a new AddressBook.")
        return AddressBook()
    except Exception as e:
        print(colored_message(f"Error loading data from '{filename}': {e}. Creating a new AddressBook.", RED_COLOR))
        return AddressBook()
    
def command_desc(command, desc, usage=None, example=None):
    def decorator(func):
        func.command = command
        func.desc = desc
        func.usage = usage
        func.example = example
        return func
    return decorator


def suggest_command(command: str, commands: list[str], limit: int = 3):
    """
    Return top N most similar commands using SequenceMatcher ratio.
    """
    similarity = []

    for cmd in commands:
        score = difflib.SequenceMatcher(None, command, cmd).ratio()
        similarity.append((cmd, score))

    # Sort by descending similarity score
    similarity.sort(key=lambda x: x[1], reverse=True)

    # Return only truly similar commands
    result = [cmd for cmd, score in similarity if score > 0.45][:limit]

    return result


def print_help(command: str, usage: str, description: str,
               example: str = None) -> str:
    """Return formatted help string for a command."""
    lines = []
    # Top border
    line = "─" * 50
    lines.append(colored_message(line, CYAN_COLOR))
    lines.append(colored_message(f"  HELP: {command}", CYAN_COLOR))
    lines.append(colored_message(line, CYAN_COLOR))
    lines.append("")

    # Usage
    lines.append(colored_message("USAGE:", YELLOW_COLOR))
    lines.append(f"  {usage}\n")

    # Description
    lines.append(colored_message("DESCRIPTION:", YELLOW_COLOR))
    lines.append(f"  {description}\n")

    # Example (optional section)
    if example:
        lines.append(colored_message("EXAMPLE:", YELLOW_COLOR))
        lines.append(f"  {example}\n")

    return "\n".join(lines)
