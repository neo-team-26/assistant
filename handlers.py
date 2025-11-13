from typing import List

from address_book import AddressBook, Record
from utils import colored_message, GREEN_COLOR, input_error, RED_COLOR
from typing import List


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


# Mapping of command names to their handler functions
COMMANDS = {
    # TODO: uncomment it after implementing the functions
    "add": add_contact,
    # "change": change_contact,
    "delete": delete_contact,
    "phone": show_phone,
    "all": show_all,
    # "add-birthday": add_birthday,
    # "show-birthday": show_birthday,
    # "birthdays": birthdays,
    "add-email": add_email,
    "remove-email": remove_email,
    "change-email": change_email,
    "add-address": add_address,
    "remove-address": remove_address,
    "change-address": change_address,
}

