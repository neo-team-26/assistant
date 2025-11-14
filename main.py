import inspect
from typing import Any, Dict
from handlers import COMMANDS
from utils import (
    parse_input,
    colored_message,
    load_addressbook,
    load_notes,
    save_all,
    Color,
    suggest_command,
)


book = load_addressbook()
notes = load_notes()

TARGETS: Dict[type, Any] = {
    type(book): book,
    type(notes): notes
}


def main() -> None:
    """
    Main command loop: loads data, processes user commands, saves on exit.
    """
    print("Welcome to the assistant bot!")
    print("Type 'help' to see available commands. Type 'exit' or 'close' to quit.")

    try:
        while True:
            try:
                user_input: str = input("Enter a command: ").strip()
            except (EOFError, KeyboardInterrupt):
                print(colored_message("\nGood bye!", Color.GREEN))
                break

            if not user_input:
                continue

            command, args = parse_input(user_input)

            if command in ("exit", "close"):
                print(colored_message("Good bye!", Color.GREEN))
                break

            handler = COMMANDS.get(command)
            if handler is None:
                print(colored_message("Invalid command.", Color.RED))
                suggestions = suggest_command(command, list(COMMANDS.keys()))
                if suggestions:
                    print("\nThe most similar commands are:")
                    for s in suggestions:
                        print(f"  {s}")
                    print()
                else:
                    print(colored_message("No similar commands found.", Color.YELLOW))
                continue

            sig = inspect.signature(handler)
            params = list(sig.parameters.values())

            if len(params) > 1 and params[1].annotation in TARGETS:
                target = TARGETS[params[1].annotation]
            else:
                target = None

            try:
                print(handler(args, target))
            except Exception as e:
                print(colored_message(str(e), Color.RED))

    finally:
        save_all(book, notes)


if __name__ == "__main__":
    main()
