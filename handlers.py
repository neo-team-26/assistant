from typing import List

from address_book import AddressBook, Record
from utils import colored_message, GREEN_COLOR, YELLOW_COLOR, CYAN_COLOR, command_desc, input_error, print_help
from typing import List

@command_desc(
    command="add",
    usage="add [name] [phone]",
    desc="Adds a new contact with the specified name and phone number.",
    example="add John 1234567890"
)
@input_error
def add_contact(args: List[str], book: AddressBook) -> str:
    if len(args) < 2:
        raise ValueError("Must provide name and phone number.")
    if len(args) > 2:
        raise ValueError("Too many arguments. Expected: [name] [phone]")

    name, phone = args

    # Check if the phone number is already registered to a different contact
    owner_record = book.find_record_by_phone(phone)

    if owner_record is not None:
        if owner_record.name.value.lower() != name.lower():
            # Phone is registered to a different contact
            raise ValueError(f"Phone number '{phone}' is already registered to contact '{owner_record.name.value}'.")
        else:
            # Phone is already registered to THIS contact (Record.add_phone will raise if duplicate for same user)
            pass

    record = book.find_record_by_name(name)
    message = "Contact updated."

    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."

    record.add_phone(phone) # This handles validation and duplicate check for the same contact

    return colored_message(message, GREEN_COLOR)


@command_desc(
    command="phone",
    usage="phone [name]",
    desc="Displays all phone numbers associated with the specified contact.",
    example="phone John"
)
@input_error
def show_phone(args: List[str], book: AddressBook) -> str:
    if len(args) < 1:
        raise ValueError("Must provide contact name.")
    if len(args) > 1:
        raise ValueError("Too many arguments. Expected: [name]")

    name = args[0]
    record = book.find_record_by_name(name)

    if record is None:
        raise KeyError(f"Contact name '{name}' not found.")

    if not record.phones:
        return f"Contact {name} has no phones saved."

    return f"{name}: {'; '.join(p.value for p in record.phones)}"


@command_desc(
    command="all",
    usage="all",
    desc="Displays all contacts stored in the address book.",
    example="all"
)
@input_error
def show_all(args: List[str], book: AddressBook) -> str:
    if args:
        raise ValueError("The 'all' command does not require arguments.")

    if not book:
        return "No contacts saved."

    all_contacts: List[str] = []
    for record in book.data.values():
        all_contacts.append(str(record))

    return "\n".join(all_contacts)


@command_desc(
    command="add-email",
    usage="add-email [name] [email]",
    desc="Adds an email address to the specified contact.",
    example="add-email John john@example.com"
)
@input_error
def add_email(args: List[str], book: AddressBook) -> str:
    if len(args) < 2:
        raise ValueError("Must provide name and email.")
    if len(args) > 2:
        raise ValueError("Too many arguments. Expected: [name] [email]")

    name, email = args

    owner_record = book.find_record_by_email(email)

    if owner_record is not None:
        if owner_record.name.value.lower() != name.lower():
            raise ValueError(f"Email '{email}' is already registered to contact '{owner_record.name.value}'.")
        else:
            pass

    record = book.find_record_by_name(name)
    message = "Contact updated."

    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."

    record.add_email(email)

    return colored_message(message, GREEN_COLOR)


@command_desc(
    command="remove-email",
    usage="remove-email [name] [email]",
    desc="Removes the specified email address from the contact.",
    example="remove-email John john@example.com"
)
@input_error
def remove_email(args: List[str], book: AddressBook) -> str:
    if len(args) < 2:
        raise ValueError("Must provide name and email.")
    if len(args) > 2:
        raise ValueError("Too many arguments. Expected: [name] [email]")

    name, email = args
    record = book.find_record_by_name(name)
    if record is None:
        raise KeyError(f"Contact name '{name}' not found.")

    record.remove_email(email)
    return colored_message("Email removed.", GREEN_COLOR)


@command_desc(
    command="change-email",
    usage="change-email [name] [old_email] [new_email]",
    desc="Changes the email address of the specified contact.",
    example="change-email John old@example.com new@example.com"
)
@input_error
def change_email(args: List[str], book: AddressBook) -> str:
    if len(args) < 3:
        raise ValueError("Must provide name, old_email and new_email.")
    if len(args) > 3:
        raise ValueError("Too many arguments. Expected: [name] [old_email] [new_email]")

    name, old_email, new_email = args
    record = book.find_record_by_name(name)
    if record is None:
        raise KeyError(f"Contact name '{name}' not found.")

    record.edit_email(old_email, new_email)
    return colored_message("Email changed.", GREEN_COLOR)


@command_desc(
    command="add-address",
    usage="add-address [name] [address]",
    desc="Adds a physical address to the specified contact.",
    example="add-address John 123 Main St"
)
@input_error
def add_address(args: List[str], book: AddressBook) -> str:
    if len(args) < 2:
        raise ValueError("Must provide name and address.")
    if len(args) > 2:
        raise ValueError("Too many arguments. Expected: [name] [address]")

    name, address = args
    record = book.find_record_by_name(name)
    message = "Contact updated."

    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."

    record.add_address(address)

    return colored_message(message, GREEN_COLOR)


@command_desc(
    command="remove-address",
    usage="remove-address [name] [address]",
    desc="Removes the specified physical address from the contact.",
    example="remove-address John 123 Main St"
)
@input_error
def remove_address(args: List[str], book: AddressBook) -> str:
    if len(args) < 2:
        raise ValueError("Must provide name and address.")
    if len(args) > 2:
        raise ValueError("Too many arguments. Expected: [name] [address]")

    name, address = args
    record = book.find_record_by_name(name)
    if record is None:
        raise KeyError(f"Contact name '{name}' not found.")

    record.remove_address(address)
    return colored_message("Address removed.", GREEN_COLOR)


@command_desc(
    command="change-address",
    usage="change-address [name] [old_address] [new_address]",
    desc="Changes the physical address of the specified contact.",
    example="change-address John 123 Old St 456 New St"
)
@input_error
def change_address(args: List[str], book: AddressBook) -> str:
    if len(args) < 3:
        raise ValueError("Must provide name, old_address and new_address.")
    if len(args) > 3:
        raise ValueError("Too many arguments. Expected: [name] [old_address] [new_address]")

    name, old_address, new_address = args
    record = book.find_record_by_name(name)
    if record is None:
        raise KeyError(f"Contact name '{name}' not found.")

    record.edit_address(old_address, new_address)
    return colored_message("Address changed.", GREEN_COLOR)


@command_desc(
    command="delete",
    usage="delete [name] or delete [name] [phone]",
    desc="Deletes the specified contact or deletes the specified phone number.",
    example="delete John or delete John 1234567890"
)
@input_error
def delete_contact(args: List[str], book: AddressBook) -> str:
    attr_len = len(args)
    if attr_len < 1 or attr_len > 3:
        raise ValueError("""To delete record please set record name as argument.
To delete phone please set record name and phone number as arguments""")
    name = args[0]
    if attr_len == 2:
        phone = args[1]
        record = book.find_record_by_name(name)
        if record:
            record.remove_phone(phone)
            return colored_message(f"Phone {phone} deleted for record {name}.", GREEN_COLOR)
        raise ValueError(f"Record {name} was not found")
    else:
        book.delete(name)
        return colored_message(f"Record {name} deleted.", GREEN_COLOR)


@command_desc(
    command="help",
    usage="help [command]",
    desc="Show help information for commands.",
    example="help add"
)
@input_error
def show_help(args: List[str], book: AddressBook) -> str:
    """Show help information for commands.

    If args provided, show detailed help for that command.
    Else, show a summary of all commands.
    """
    if len(args) > 1:
        raise ValueError("Too many arguments. Expected: [command]")
    if len(args) == 1:
        command_name = args[0]
        handler = COMMANDS.get(command_name)
        if handler is None:
            raise KeyError(f"Command '{command_name}' not found.")
        return print_help(
            command=handler.command,
            usage=handler.usage,
            description=handler.desc,
            example=handler.example
        )
    else:
        # Show summary of all commands
        summary_lines: List[str] = []
        for cmd_name, handler in COMMANDS.items():
            line = (colored_message(f"{cmd_name}:", CYAN_COLOR) +
                    f" {handler.desc}")
            summary_lines.append(line)
        return "\n".join(summary_lines)


# Mapping of command names to their handler functions
@command_desc(
    command="add-birthday",
    usage="add-birthday [name] [DD.MM.YYYY]",
    desc="Adds a birthday to a contact (creates contact if missing).",
    example="add-birthday John 01.01.1990"
)
@input_error
def add_birthday(args: List[str], book: AddressBook) -> str:
    """Add a birthday to a contact. If contact doesn't exist, create it."""
    if len(args) < 2:
        raise ValueError("Must provide name and birthday date.")
    if len(args) > 2:
        raise ValueError("Too many arguments. Expected: [name] [DD.MM.YYYY]")

    name, birthday_date = args
    record = book.find_record_by_name(name)
    message = "Birthday added."

    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."

    record.add_birthday(birthday_date)
    return colored_message(message, GREEN_COLOR)


@command_desc(
    command="show-birthday",
    usage="show-birthday [name]",
    desc="Displays the specified contact's birthday.",
    example="show-birthday John"
)
@input_error
def show_birthday(args: List[str], book: AddressBook) -> str:
    """Show a contact's birthday in DD.MM.YYYY format."""
    if len(args) < 1:
        raise ValueError("Must provide contact name.")
    if len(args) > 1:
        raise ValueError("Too many arguments. Expected: [name]")

    name = args[0]
    record = book.find_record_by_name(name)
    if record is None:
        raise KeyError(f"Contact name '{name}' not found.")

    if not record.birthday:
        return f"Contact {name} has no birthday saved."

    return f"{name}: {record.birthday}"


@command_desc(
    command="birthdays",
    usage="birthdays [days]",
    desc="Lists upcoming birthdays grouped by weekday.",
    example="birthdays 7"
)
@input_error
def birthdays(args: List[str], book: AddressBook) -> str:
    """List upcoming birthdays grouped by weekday. Optional single arg: days (int)."""
    if len(args) > 1:
        raise ValueError("Too many arguments. Expected: [days]")

    days = 7
    if len(args) == 1:
        try:
            days = int(args[0])
        except ValueError:
            raise ValueError("Days must be an integer.")
        if days <= 0:
            raise ValueError("Days must be a positive integer.")

    upcoming = book.get_upcoming_birthdays(days=days)
    if not upcoming:
        return "No upcoming birthdays found."

    lines: List[str] = []
    for day, names in upcoming.items():
        lines.append(f"{day}: {', '.join(names)}")

    return "\n".join(lines)
 


COMMANDS = {
    # TODO: uncomment it after implementing the functions
    "add": add_contact,
    # "change": change_contact,
    "delete": delete_contact,
    "phone": show_phone,
    "all": show_all,
    "add-birthday": add_birthday,
    "show-birthday": show_birthday,
    "birthdays": birthdays,
    "add-email": add_email,
    "remove-email": remove_email,
    "change-email": change_email,
    "add-address": add_address,
    "remove-address": remove_address,
    "change-address": change_address,
    "help": show_help,
}

