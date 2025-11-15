from address_book import AddressBook, Record
from notebook import Notebook
from utils import colored_message, Color, command_desc, input_error, print_help, Handler
from typing import List, Optional


def resolve_contact_by_name(name: str, book: AddressBook) -> Optional[Record]:
    matches = book.find_all_records_by_name(name)
    
    if not matches:
        return None
    
    if len(matches) == 1:
        return matches[0]
    
    print(f"\n{len(matches)} contact(s) found with name '{name}':")
    for record in matches:
        parts: List[str] = [f"ID: {record.contact_id}"]

        if record.phones:
            parts.append(f"Phones: {', '.join(p.value for p in record.phones)}")

        if record.emails:
            parts.append(f"Emails: {', '.join(e.value for e in record.emails)}")

        if record.addresses:
            parts.append(f"Addresses: {', '.join(a.value for a in record.addresses)}")

        if record.birthday:
            parts.append(f"Birthday: {record.birthday}")

        print(f"  {record.name.value} | " + " | ".join(parts))
    
    try:
        contact_id = input("\nEnter the Contact ID to select: ").strip()
    except KeyboardInterrupt:
        raise KeyboardInterrupt("\nOperation cancelled by user.")
    selected = book.find_record_by_contact_id(contact_id)
    
    if selected is None:
        raise ValueError(f"Contact ID '{contact_id}' not found.")
    
    return selected


@command_desc(
    command="create-contact",
    usage="create-contact [name] [phone]",
    desc="Creates a new contact with the specified name and phone number.",
    example="create-contact John 1234567890"
)
@input_error
def create_contact(args: List[str], book: AddressBook) -> str:
    if len(args) != 2:
        raise ValueError("Must provide contact name and phone number.")

    name, phone = args

    owner_record = book.find_record_by_phone(phone)
    if owner_record is not None:
        raise ValueError(f"Phone number '{phone}' is already registered to contact '{owner_record.name.value}'.")

    record = Record(name)
    record.add_phone(phone)
    book.add_record(record)

    return colored_message(f"Contact '{name}' created (ID: {record.contact_id}) with phone {phone}.", Color.GREEN)


@command_desc(
    command="create-contact-wizard",
    usage="create-contact-wizard",
    desc="Interactive command to create a new contact with multiple fields (name, phone, birthday, email, address).",
    example="create-contact-wizard"
)
def create_contact_wizard(args: List[str], book: AddressBook) -> str:
    if args:
        raise ValueError("The 'create-contact-wizard' command does not require arguments.")

    print("Enter contact details. Required fields are marked with *")
    name = input("* Contact name: ").strip()
    if not name:
        raise ValueError("Contact name is required.")

    phone_input = input("* Phone number (10 digits): ").strip()
    if not phone_input:
        raise ValueError("Phone number is required.")
    
    try:
        owner_record = book.find_record_by_phone(phone_input)
        if owner_record is not None:
            raise ValueError(f"Phone number '{phone_input}' is already registered to contact '{owner_record.name.value}'.")
    except ValueError as e:
        raise ValueError(f"Invalid phone: {e}")

    record = Record(name)

    try:
        record.add_phone(phone_input)
    except ValueError as e:
        raise ValueError(f"Invalid phone: {e}")

    birthday_input = input("  Birthday (DD.MM.YYYY, optional): ").strip()
    if birthday_input:
        try:
            record.add_birthday(birthday_input)
        except ValueError as e:
            raise ValueError(f"Invalid birthday: {e}")

    email_input = input("  Email (optional): ").strip()
    if email_input:
        try:
            record.add_email(email_input)
        except ValueError as e:
            raise ValueError(f"Invalid email: {e}")

    address_input = input("  Address (optional): ").strip()
    if address_input:
        try:
            record.add_address(address_input)
        except ValueError as e:
            raise ValueError(f"Invalid address: {e}")

    book.add_record(record)

    return colored_message(f"Contact '{name}' (ID: {record.contact_id}) added successfully with all details.", Color.GREEN)


@command_desc(
    command="show-phone",
    usage="show-phone [name]",
    desc="Shows phone numbers of all contacts by this name.",
    example="show-phone John"
)
@input_error
def show_phone(args: List[str], book: AddressBook) -> str:
    if len(args) < 1:
        raise ValueError("Must provide contact name.")
    if len(args) > 1:
        raise ValueError("Too many arguments. Expected: [name]")
    name = args[0]
    matches = book.find_all_records_by_name(name)

    if not matches:
        raise KeyError(f"Contact name '{name}' not found.")

    if len(matches) == 1:
        single = matches[0]
        if single.phones:
            return '; '.join(p.value for p in single.phones)
        return f"Contact {single.name.value} (ID: {single.contact_id}) has no phones saved."

    # Multiple matches: collect detailed info
    lines: List[str] = []
    for record in matches:
        parts: List[str] = []
        parts.append(f"{record.name.value} (ID: {record.contact_id})")

        if record.phones:
            parts.append(f"phones: {'; '.join(p.value for p in record.phones)}")

        if record.emails:
            parts.append(f"emails: {'; '.join(e.value for e in record.emails)}")

        if record.addresses:
            parts.append(f"addresses: {'; '.join(a.value for a in record.addresses)}")

        if record.birthday:
            parts.append(f"birthday: {record.birthday}")

        lines.append(', '.join(parts))

    return "\n".join(lines)


@command_desc(
    command="add-phone",
    usage="add-phone [name] [phone]",
    desc="Adds a phone number to the specified contact.",
    example="add-phone John 9876543210"
)
@input_error
def add_phone(args: List[str], book: AddressBook) -> str:
    if len(args) != 2:
        raise ValueError("Must provide contact name and phone number.")
    
    name, phone = args
    
    owner_record = book.find_record_by_phone(phone)
    if owner_record is not None:
        raise ValueError(f"Phone number '{phone}' is already registered to contact '{owner_record.name.value}'.")
    
    record = resolve_contact_by_name(name, book)
    if record is None:
        raise KeyError(f"Contact name '{name}' not found.")
    
    record.add_phone(phone)
    return colored_message(f"Phone {phone} added to contact {name} (ID: {record.contact_id}).", Color.GREEN)

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

    record = resolve_contact_by_name(name, book)
    message = "Contact updated."

    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."

    record.add_email(email)

    return colored_message(message, Color.GREEN)


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
    record = resolve_contact_by_name(name, book)
    if record is None:
        raise KeyError(f"Contact name '{name}' not found.")

    record.remove_email(email)
    return colored_message(f"Email removed from contact {name} (ID: {record.contact_id}).", Color.GREEN)


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
    record = resolve_contact_by_name(name, book)
    if record is None:
        raise KeyError(f"Contact name '{name}' not found.")

    record.edit_email(old_email, new_email)
    return colored_message(f"Email changed for contact {name} (ID: {record.contact_id}).", Color.GREEN)


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
    record = resolve_contact_by_name(name, book)
    if record is None:
        raise KeyError(f"Contact name '{name}' not found.")

    record.add_address(address)

    return colored_message(f"Address added to contact {name} (ID: {record.contact_id}).", Color.GREEN)


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
    record = resolve_contact_by_name(name, book)
    if record is None:
        raise KeyError(f"Contact name '{name}' not found.")

    record.remove_address(address)
    return colored_message(f"Address removed from contact {name} (ID: {record.contact_id}).", Color.GREEN)


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
    record = resolve_contact_by_name(name, book)
    if record is None:
        raise KeyError(f"Contact name '{name}' not found.")

    record.edit_address(old_address, new_address)
    return colored_message(f"Address changed for contact {name} (ID: {record.contact_id}).", Color.GREEN)


@command_desc(
    command="delete-contact",
    usage="delete-contact [name]",
    desc="Deletes the specified contact.",
    example="delete-contact John"
)
@input_error
def delete_contact(args: List[str], book: AddressBook) -> str:
    if len(args) != 1:
        raise ValueError("Must provide contact name.")
    name = args[0]
    matches = book.find_all_records_by_name(name)

    if not matches:
        raise KeyError(f"Contact name '{name}' not found.")

    if len(matches) == 1:
        record = matches[0]
    else:
        record = resolve_contact_by_name(name, book)
        if record is None:
            raise KeyError(f"Contact name '{name}' not found.")

    book.delete(record.contact_id)
    return colored_message(f"Contact {record.name.value} (ID: {record.contact_id}) deleted.", Color.GREEN)


@command_desc(
    command="delete-phone",
    usage="delete-phone [name] [phone]",
    desc="Deletes the specified phone number from a contact.",
    example="delete-phone John 1234567890"
)
@input_error
def delete_phone(args: List[str], book: AddressBook) -> str:
    if len(args) != 2:
        raise ValueError("Must provide name and phone number.")
    name, phone = args
    record = book.find_record_by_phone(phone)
    if record is None:
        raise KeyError(f"Contact with phonenumber '{phone}' not found.")
    
    if len(record.phones) == 1:
        raise ValueError(f"Cannot delete the last phone number for '{name}'. To remove this contact entirely, use 'delete-contact {name}'.")
    
    record.remove_phone(phone)
    return colored_message(f"Phone {phone} deleted for record {name} (ID: {record.contact_id}).", Color.GREEN)


@command_desc(
    command="add-note",
    usage="add-note [name] [text] [optional #tag1 #tag2 ...]",
    desc="Adds note to notebook with specified name and optional tags (starting with #).",
    example="add-note homework 'Do it today!!!' #todo #urgent"
)
@input_error
def add_note(args: List[str], notebook: Notebook) -> str:
    if len(args) < 2:
        raise ValueError("Please provide Note name and text (in quotation marks). Optional: add tags starting with #.")

    name = args[0]
    text_parts: List[str] = []
    tags: List[str] = []

    for arg in args[1:]:
        if arg.startswith('#'):
            tags.append(arg[1:]) # Видаляємо #
        elif not tags: # All text parts before tags
            text_parts.append(arg)
        else: # If tags have started, no more text allowed
            raise ValueError("Text must be provided before tags. Tags must start with '#'.")

    if not text_parts:
        raise ValueError("Please provide Note text (in quotation marks).")

    text = " ".join(text_parts)

    notebook.add_note(name, text, tags)

    tag_info = f" with tags: {', '.join(tags)}" if tags else ""
    return colored_message(f"Added note \"{name}\" with text: \"{text}\"{tag_info}", Color.GREEN)


@command_desc(
    command="edit-note",
    usage="edit-note [name] [text]",
    desc="Changes note in notebook for specified name.",
    example="edit-note homework 'Do it today!!!'"
)
@input_error
def edit_note(args: List[str], notebook: Notebook) -> str:
    if len(args) != 2:
        raise ValueError("Please provide note name and text(in quotation marks)")
    name, text = args
    notebook.edit_note(name, text)
    return colored_message(f"Changed note {name} to:{text}", Color.GREEN)


@command_desc(
    command="delete-note",
    usage="delete-note [name]",
    desc="Deletes note with specified name in notebook.",
    example="delete-note homework"
)
@input_error
def delete_note(args: List[str], notebook: Notebook) -> str:
    if len(args) != 1:
        raise ValueError("Please provide note name")
    name = args[0]
    notebook.delete_note(name)
    return colored_message(f"Deleted note {name}", Color.GREEN)


@command_desc(
    command="all-notes",
    usage="all-notes",
    desc="Lists all notes in notebook.",
    example="all-notes"
)
@input_error
def all_notes(args: List[str], notebook: Notebook) -> str:
    if args:
        raise ValueError("The 'all-notes' command does not require arguments.")
    if not notebook:
        return "No notes saved."
    return notebook.list_notes()


@command_desc(
    command="find-notes",
    usage="find-notes [word | +word | -word] [optional #tag1 #tag2 ...]",
    desc="Lists notes that match keywords (+ for AND, - for NOT, no prefix for OR) AND AT LEAST ONE specified tag.",
    example="find-notes report +financial -draft #urgent #month_end"
)
@input_error
def find_notes(args: List[str], notebook: Notebook) -> str:
    if not args:
        raise ValueError("Please provide one or more search words or tags.")
    if not notebook:
        return "No notes available."

    and_words: List[str] = []
    or_words: List[str] = []
    not_words: List[str] = []
    required_tags: List[str] = []

    for arg in args:
        if arg.startswith('#'):
            required_tags.append(arg[1:])
        elif arg.startswith('+'):
            and_words.append(arg[1:])
        elif arg.startswith('-'):
            not_words.append(arg[1:])
        else:
            or_words.append(arg)

    if not (and_words or or_words or not_words or required_tags):
        raise ValueError("Please provide one or more search words or tags.")

    results = notebook.find_notes(and_words, or_words, not_words, required_tags)

    if not results:
        text_terms = ", ".join(and_words + or_words + not_words)
        tag_terms = ", ".join(required_tags)

        message = "No matching notes found."
        if text_terms:
            message += f" for text: {text_terms}"
        if tag_terms:
            message += f" and tags: {tag_terms}"

        return message

    lines: List[str] = [f"{name}: {text}" for name, text in results]
    return "\n".join(lines)


@command_desc(
    command="show-note",
    usage="show-note [name]",
    desc="Shows note with specified name",
    example="show-note homework"
)
@input_error
def show_note(args: List[str], notebook: Notebook) -> str:
    if len(args) != 1:
        raise ValueError("Please provide note name")
    name = args[0]
    note = notebook.get_note(name)
    if note is None:
        return colored_message(f"Note '{name}' not found.", Color.RED)
    return note


@command_desc(
    command="add-tags",
    usage="add-tags [name] [#tag1 #tag2 ...]",
    desc="Adds one or more tags to the specified note.",
    example="add-tags homework #urgent #high_priority"
)
@input_error
def add_tags(args: List[str], notebook: Notebook) -> str:
    if len(args) < 2:
        raise ValueError("Please provide note name and at least one tag (starting with #).")

    name = args[0]
    tags: List[str] = []

    for arg in args[1:]:
        if arg.startswith('#'):
            tags.append(arg[1:])
        else:
            raise ValueError("All tags must start with '#'.")

    if not tags:
        raise ValueError("Please provide at least one tag (starting with #).")

    try:
        notebook.add_tags_to_note(name, tags)
        return colored_message(f"Tags added to note '{name}': {', '.join(tags)}", Color.GREEN)
    except KeyError as e:
        raise KeyError(str(e))


@command_desc(
    command="remove-tag",
    usage="remove-tag [name] [#tag]",
    desc="Removes a specific tag from the note.",
    example="remove-tag homework #urgent"
)
@input_error
def remove_tag(args: List[str], notebook: Notebook) -> str:
    if len(args) != 2:
        raise ValueError("Please provide note name and one tag (starting with #).")

    name = args[0]
    tag_arg = args[1]

    if not tag_arg.startswith('#'):
        raise ValueError("The tag must start with '#'.")

    tag = tag_arg[1:]

    try:
        notebook.remove_tag_from_note(name, tag)
        return colored_message(f"Tag '{tag}' removed from note '{name}'.", Color.GREEN)
    except KeyError as e:
        raise KeyError(str(e))
    except ValueError as e:
        raise ValueError(str(e))


@command_desc(
    command="help",
    usage="help [command]",
    desc="Show help information for commands.",
    example="help add"
)
@input_error
def show_help(args: List[str], _: None) -> str: # Second argument is needed for uniformity
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
        # Use getattr to access metadata attached by decorator to avoid mypy attribute errors
        return print_help(
            command=getattr(handler, 'command', command_name),
            usage=getattr(handler, 'usage', ''),
            description=getattr(handler, 'desc', ''),
            example=getattr(handler, 'example', None)
        )
    else:
        # Show summary of all commands
        summary_lines: List[str] = []
        for cmd_name, handler in COMMANDS.items():
            line = (colored_message(f"{cmd_name}:", Color.CYAN) +
                    f" {getattr(handler, 'desc', '')}")
            summary_lines.append(line)
        return "\n".join(summary_lines)


@command_desc(
    command="update-phone",
    usage="chpdate-phone [name] [old_phone] [new_phone]",
    desc="Updates an existing phone number for a contact.",
    example="update-phone John 0123456789 0987654321"
)
@input_error
def update_phone(args: List[str], book: AddressBook) -> str:
    if len(args) < 3:
        raise ValueError("Must provide name, old phone and new phone.")
    if len(args) > 3:
        raise ValueError("Too many arguments. Expected: [name] [old_phone] [new_phone]")

    name, old_phone, new_phone = args

    owner_record = book.find_record_by_phone(new_phone)
    if owner_record is not None and owner_record.name.value.lower() != name.lower():
        raise ValueError(f"Phone number '{new_phone}' is already registered to contact '{owner_record.name.value}'.")

    record = book.find_record_by_phone(old_phone)
    record.edit_phone(old_phone, new_phone)
    return colored_message(f"Phone changed for contact {name} (ID: {record.contact_id}).", Color.GREEN)


@command_desc(
    command="update-name",
    usage="update-name [old_name] [new_name]",
    desc="Updates a contact's name.",
    example="update-name John Johnny"
)
@input_error
def update_name(args: List[str], book: AddressBook) -> str:
    if len(args) < 2:
        raise ValueError("Must provide old name and new name.")
    if len(args) > 2:
        raise ValueError("Too many arguments. Expected: [old_name] [new_name]")

    old_name, new_name = args

    record = resolve_contact_by_name(old_name, book)
    if record is None:
        raise KeyError(f"Contact name '{old_name}' not found.")

    old_id = record.contact_id
    record.name.value = new_name

    return colored_message(f"Contact name changed from '{old_name}' to '{new_name}' (ID: {old_id}).", Color.GREEN)


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
    record = resolve_contact_by_name(name, book)
    message = "Birthday added."

    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."

    record.add_birthday(birthday_date)
    return colored_message(f"{message} (ID: {record.contact_id})", Color.GREEN)


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
    matches = book.find_all_records_by_name(name)

    if not matches:
        raise KeyError(f"Contact name '{name}' not found.")

    if len(matches) == 1:
        single = matches[0]
        if single.birthday:
            return f"Birthday: {single.birthday}."
        return f"Contact {single.name.value} (ID: {single.contact_id}) has no birthday saved."

    # Multiple matches: collect detailed info
    lines: List[str] = []
    for record in matches:
        parts: List[str] = []
        parts.append(f"{record.name.value} (ID: {record.contact_id})")

        if record.birthday:
            parts.append(f"birthday: {record.birthday}")
        else:
            parts.append("birthday: N/A")

        if record.phones:
            parts.append(f"phones: {'; '.join(p.value for p in record.phones)}")

        if record.emails:
            parts.append(f"emails: {'; '.join(e.value for e in record.emails)}")

        if record.addresses:
            parts.append(f"addresses: {'; '.join(a.value for a in record.addresses)}")

        lines.append(', '.join(parts))

    return "\n".join(lines)


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


@command_desc(
    command="update-birthday",
    usage="update-birthday [name] [DD.MM.YYYY]",
    desc="Updates an existing birthday for a contact.",
    example="update-birthday John 15.06.1985"
)
@input_error
def update_birthday(args: List[str], book: AddressBook) -> str:
    if len(args) < 2:
        raise ValueError("Must provide name and birthday date.")
    if len(args) > 2:
        raise ValueError("Too many arguments. Expected: [name] [DD.MM.YYYY]")

    name, birthday_date = args
    record = resolve_contact_by_name(name, book)
    if record is None:
        raise KeyError(f"Contact name '{name}' not found.")

    if not record.birthday:
        raise ValueError(f"Contact '{name}' does not have a birthday set.")

    record.birthday.value = birthday_date
    return colored_message(f"Birthday updated for {name} (ID: {record.contact_id}).", Color.GREEN)


@command_desc(
    command="delete-birthday",
    usage="delete-birthday [name]",
    desc="Deletes the birthday from a contact.",
    example="delete-birthday John"
)
@input_error
def delete_birthday(args: List[str], book: AddressBook) -> str:
    if len(args) < 1:
        raise ValueError("Must provide contact name.")
    if len(args) > 1:
        raise ValueError("Too many arguments. Expected: [name]")

    name = args[0]
    record = resolve_contact_by_name(name, book)
    if record is None:
        raise KeyError(f"Contact name '{name}' not found.")

    if not record.birthday:
        raise ValueError(f"Contact '{name}' does not have a birthday set.")

    record.birthday = None
    return colored_message(f"Birthday removed for {name} (ID: {record.contact_id}).", Color.GREEN)


@command_desc(
    command="find-contact",
    usage="find-contact [field] [value]",
    desc="Find a contact by name, phone, address, or birthday.",
    example="find-contact phone 0123456789"
)
@input_error
def find_contact(args: List[str], book: AddressBook) -> str:
    if len(args) < 2:
        raise ValueError("Must provide field and value. Usage: find-contact [field] [value]")
    if len(args) > 2:
        raise ValueError("Too many arguments. Usage: find-contact [field] [value]")

    field, value = args
    field = field.lower()
    found: list[Record] = []

    if field == "name":
        found = book.find_all_records_by_name(value)
    elif field == "phone":
        rec = book.find_record_by_phone(value)
        if rec:
            found.append(rec)
    elif field == "address":
        for rec in book.data.values():
            if any(addr.value == value for addr in rec.addresses):
                found.append(rec)
    elif field == "birthday":
        for rec in book.data.values():
            if rec.birthday and str(rec.birthday) == value:
                found.append(rec)
    else:
        raise ValueError("Field must be one of: name, phone, address, birthday.")

    if not found:
        return f"No contact found for {field}: {value}"
    return "\n".join(str(r) for r in found)

COMMANDS: dict[str, Handler] = {
    # TODO: uncomment it after implementing the functions
    "all": show_all,
    "find-contact": find_contact,
    "create-contact": create_contact,
    "create-contact-wizard": create_contact_wizard,
    "delete-contact": delete_contact,
    "update-name": update_name,
    "show-phone": show_phone,
    "add-phone": add_phone,
    "update-phone": update_phone,
    "delete-phone": delete_phone,
    "show-birthday": show_birthday,
    "add-birthday": add_birthday,
    "update-birthday": update_birthday,
    "delete-birthday": delete_birthday,
    "birthdays": birthdays,
    "add-email": add_email,
    "remove-email": remove_email,
    "change-email": change_email,
    "add-address": add_address,
    "remove-address": remove_address,
    "change-address": change_address,
    "add-note": add_note,
    "edit-note": edit_note,
    "delete-note": delete_note,
    "all-notes": all_notes,
    "find-notes": find_notes,
    "show-note": show_note,
    "help": show_help,
    "add-tags": add_tags,
    "remove-tag": remove_tag,
}
