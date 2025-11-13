from typing import List

from address_book import AddressBook, Record
from utils import colored_message, GREEN_COLOR


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
def show_all(args: List[str], book: AddressBook) -> str:
    if args:
        raise ValueError("The 'all' command does not require arguments.")

    if not book:
        return "No contacts saved."

    all_contacts: List[str] = []
    for record in book.data.values():
        all_contacts.append(str(record))

    return "\n".join(all_contacts)

# Mapping of command names to their handler functions
COMMANDS = {
    # TODO: uncomment it after implementing the functions
    "add": add_contact,
    # "change": change_contact,
    # "phone": show_phone,
    "all": show_all,
    # "add-birthday": add_birthday,
    # "show-birthday": show_birthday,
    # "birthdays": birthdays,
}