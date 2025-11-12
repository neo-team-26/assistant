import pickle
from typing import List, Optional, Literal, Tuple

# --- Constants ---
from address_book import AddressBook

RED_COLOR = "\033[91m"
GREEN_COLOR = "\033[92m"
END_COLOR = "\033[0m"

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