from typing import List, Optional, Dict, Union, Any, cast
from collections import UserDict
from datetime import datetime, timedelta, date
import re
import uuid


class Field:
    """Base class for record fields."""

    def __init__(self, value: Any):
        self._value = value

    def __str__(self) -> str:
        return str(self.value)

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, new_value: Any) -> None:
        self._value = new_value


class Name(Field):
    """Class for storing the contact's name. A mandatory field."""
    pass


class Phone(Field):
    """Class for storing the phone number. Includes 10-digit format validation."""

    def __init__(self, value: str):
        self._validate_phone(value)
        super().__init__(value)

    @staticmethod
    def _validate_phone(phone_number: str) -> None:
        """Checks if the phone number is a 10-digit number."""
        if not (phone_number.isdigit() and len(phone_number) == 10):
            raise ValueError("Phone number must be a 10-digit number.")

    @property
    def value(self) -> str:
        return str(self._value)

    @value.setter
    def value(self, new_value: str) -> None:
        self._validate_phone(new_value)
        self._value = new_value


class Email(Field):
    """Class for storing the contact's email. Includes simple email format validation."""

    # Simple, commonly used email regex. Not exhaustive but sufficient for basic validation.
    EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

    def __init__(self, value: str):
        self._validate_email(value)
        super().__init__(value)

    @staticmethod
    def _validate_email(email: str) -> None:
        """Validate email using a regular expression. Raise ValueError on invalid format."""
        if not Email.EMAIL_REGEX.fullmatch(email):
            raise ValueError("Invalid email address format.")

    @property
    def value(self) -> str:
        return str(self._value)

    @value.setter
    def value(self, new_value: str) -> None:
        self._validate_email(new_value)
        self._value = new_value


class Address(Field):
    """Class for storing the contact's postal/address string. No validation required."""

    def __init__(self, value: str):
        # No validation required; store as-is
        super().__init__(value)

    @property
    def value(self) -> str:
        return str(self._value)

    @value.setter
    def value(self, new_value: str) -> None:
        # Accept any string for address
        self._value = new_value


class Birthday(Field):
    """Class for storing the contact's birthday. Includes DD.MM.YYYY format validation."""

    def __init__(self, value: str):
        self._validate_birthday(value)
        # Store as datetime.date object
        super().__init__(datetime.strptime(value, "%d.%m.%Y").date())

    @staticmethod
    def _validate_birthday(date_str: str) -> None:
        """Checks if the date string is in DD.MM.YYYY format."""
        try:
            datetime.strptime(date_str, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    @property
    def value(self) -> date:
        return cast(date, self._value)

    @value.setter
    def value(self, new_value: str) -> None:
        self._validate_birthday(new_value)
        self._value = datetime.strptime(new_value, "%d.%m.%Y").date()

    def __str__(self) -> str:
        if self._value is None:
            return ""
        # Format back to DD.MM.YYYY for display
        return cast(date, self._value).strftime("%d.%m.%Y")


class Record:
    """Class for storing contact information (name, list of phones, and birthday)."""

    def __init__(self, name: str):
        self.contact_id: str = str(uuid.uuid4())[:8]  # Short 8-char UUID for display
        self.name: Name = Name(name)
        self.phones: List[Phone] = []
        self.emails: List[Email] = []
        self.addresses: List[Address] = []
        self.birthday: Optional[Birthday] = None

    def add_phone(self, phone_number: str) -> None:
        phone = Phone(phone_number) # Validation is inside Phone.__init__
        if self.find_phone(phone_number):
            raise ValueError(f"Phone number '{phone_number}' already exists for this contact.")
        self.phones.append(phone)

    def remove_phone(self, phone_number: str) -> None:
        phone_to_remove = self.find_phone(phone_number)
        if phone_to_remove:
            self.phones.remove(phone_to_remove)
        else:
            raise ValueError(f"Phone number '{phone_number}' not found.")

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        # Check if the new phone is already used by this record
        if self.find_phone(new_phone):
            raise ValueError(f"New phone number '{new_phone}' is already registered to this contact.")

        phone_object = self.find_phone(old_phone)
        if phone_object:
            phone_object.value = new_phone
        else:
            raise ValueError(f"Old phone number '{old_phone}' not found.")

    # --- Email management ---
    def add_email(self, email_str: str) -> None:
        email = Email(email_str)  # validation inside Email
        if self.find_email(email_str):
            raise ValueError(f"Email '{email_str}' already exists for this contact.")
        self.emails.append(email)

    def remove_email(self, email_str: str) -> None:
        email_obj = self.find_email(email_str)
        if email_obj:
            self.emails.remove(email_obj)
        else:
            raise ValueError(f"Email '{email_str}' not found.")

    def edit_email(self, old_email: str, new_email: str) -> None:
        if self.find_email(new_email):
            raise ValueError(f"New email '{new_email}' is already registered to this contact.")

        email_object = self.find_email(old_email)
        if email_object:
            email_object.value = new_email
        else:
            raise ValueError(f"Old email '{old_email}' not found.")

    def find_email(self, email_str: str) -> Union[Email, None]:
        for email in self.emails:
            if email.value == email_str:
                return email
        return None

    # --- Address management ---
    def add_address(self, address_str: str) -> None:
        addr = Address(address_str)
        # Inline check for existing address (removed separate find_address helper)
        for a in self.addresses:
            if a.value == address_str:
                raise ValueError(f"Address '{address_str}' already exists for this contact.")
        self.addresses.append(addr)

    def remove_address(self, address_str: str) -> None:
        # Inline search and removal
        for a in self.addresses:
            if a.value == address_str:
                self.addresses.remove(a)
                return
        raise ValueError(f"Address '{address_str}' not found.")

    def edit_address(self, old_address: str, new_address: str) -> None:
        # Prevent duplicate
        for a in self.addresses:
            if a.value == new_address:
                raise ValueError(f"New address '{new_address}' is already registered to this contact.")

        # Find existing and edit
        for a in self.addresses:
            if a.value == old_address:
                a.value = new_address
                return

        raise ValueError(f"Old address '{old_address}' not found.")

    # find_address removed per request; address methods perform inline searches

    def find_phone(self, phone_number: str) -> Union[Phone, None]:
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None

    def add_birthday(self, birthday_date: str) -> None:
        if self.birthday is not None:
            raise ValueError("Birthday already set. Use a separate command to edit.")
        self.birthday = Birthday(birthday_date)

    def __str__(self) -> str:
        phone_str = '; '.join(p.value for p in self.phones)
        email_str = '; '.join(e.value for e in self.emails)
        addr_str = '; '.join(a.value for a in self.addresses)
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        parts = [f"Contact ID: {self.contact_id}, name: {self.name.value}"]
        parts.append(f"phones: {phone_str}")
        if email_str:
            parts.append(f"emails: {email_str}")
        if addr_str:
            parts.append(f"addresses: {addr_str}")
        parts.append(birthday_str.lstrip(', '))
        # Filter out empty parts and join with ', '
        return ', '.join([p for p in parts if p])


class AddressBook(UserDict[str, Record]):
    """Class for storing and managing records (Record). Inherits from UserDict."""

    def add_record(self, record: Record) -> None:
        contact_id = record.contact_id
        if contact_id in self.data:
            raise ValueError(f"Contact ID '{contact_id}' already exists.")
        self.data[contact_id] = record

    def find_record_by_name(self, name: str) -> Optional[Record]:
        for record in self.data.values():
            if record.name.value.lower() == name.lower():
                return record
        return None

    def find_all_records_by_name(self, name: str) -> List[Record]:
        matching = []
        for record in self.data.values():
            if record.name.value.lower() == name.lower():
                matching.append(record)
        return matching

    def find_record_by_contact_id(self, contact_id: str) -> Optional[Record]:
        for record in self.data.values():
            if record.contact_id == contact_id:
                return record
        return None

    def find_record_by_phone(self, phone: str) -> Optional[Record]:
        for record in self.data.values():
            if record.find_phone(phone):
                return record
        return None

    def find_record_by_email(self, email: str) -> Optional[Record]:
        for record in self.data.values():
            if hasattr(record, 'find_email') and record.find_email(email):
                return record
        return None

    def delete(self, contact_id: str) -> None:
        if contact_id in self.data:
            del self.data[contact_id]
        else:
            raise KeyError(f"Contact ID '{contact_id}' not found for deletion.")

    def get_upcoming_birthdays(self, days: int = 7) -> Dict[str, List[str]]:
        upcoming_birthdays: Dict[str, List[str]] = {}
        today = datetime.now().date()

        # Day names for sorting the final output
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        for record in self.data.values():
            if record.birthday is not None:
                birthday_date = record.birthday.value

                # Check for birthday this year
                birthday_this_year = birthday_date.replace(year=today.year)

                if birthday_this_year < today:
                    # Check for birthday next year if this year's has passed
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                time_delta = birthday_this_year - today

                if timedelta(0) <= time_delta < timedelta(days=days):
                    birthday_day_index = birthday_this_year.weekday() # 0=Monday, 6=Sunday

                    # Rule: If birthday is Saturday (5) or Sunday (6), move congratulations to Monday (0)
                    if birthday_day_index >= 5:
                        congratulation_date = birthday_this_year + timedelta(days=(7 - birthday_day_index))
                    else:
                        congratulation_date = birthday_this_year

                    day_name = congratulation_date.strftime("%A") # e.g., Monday
                    name = record.name.value

                    if day_name not in upcoming_birthdays:
                        upcoming_birthdays[day_name] = []

                    upcoming_birthdays[day_name].append(name)

        # Sort the results by the defined day order
        sorted_birthdays: Dict[str, List[str]] = {}
        for day in day_order:
            if day in upcoming_birthdays:
                sorted_birthdays[day] = upcoming_birthdays[day]

        return sorted_birthdays