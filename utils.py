# --- Constants ---
RED_COLOR = "\033[91m"
GREEN_COLOR = "\033[92m"
END_COLOR = "\033[0m"



def colored_message(message: str, color: str) -> str:
    """
    Cover the message in ANSI escape sequences for colored output.
    """
    return f"{color}{message}{END_COLOR}"