from utils import colored_message, GREEN_COLOR, RED_COLOR


def main() -> None:
    """
    The main function that manages the command processing loop,
    including data loading and saving.
    """

    print("Welcome to the assistant bot!")
    print("Type 'help' to see available commands. Type 'exit' or 'close' to quit.")

    while True:
        try:
            user_input: str = input("Enter a command: ").strip()
        except EOFError:
            # Handle Ctrl+D (EOF) gracefully
            print(colored_message("\nGood bye!", GREEN_COLOR))
            break

        if not user_input:
            continue

        # TODO: implement input parsing and command handling

        if user_input in ["close", "exit"]:
            print(colored_message("Good bye!", GREEN_COLOR))
            break


if __name__ == "__main__":
    main()