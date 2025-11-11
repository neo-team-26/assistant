from typing import List, Optional, Dict, Union, Any
from collections import UserDict
from datetime import datetime, timedelta


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
    def value(self, new_value: Any):
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

    @Field.value.setter
    def value(self, new_value: str):
        self._validate_phone(new_value)
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

    @Field.value.setter
    def value(self, new_value: str):
        self._validate_birthday(new_value)
        self._value = datetime.strptime(new_value, "%d.%m.%Y").date()

    def __str__(self) -> str:
        if self._value is None:
            return ""
        # Format back to DD.MM.YYYY for display
        return self._value.strftime("%d.%m.%Y")


class Record:
    """Class for storing contact information (name, list of phones, and birthday)."""

    def __init__(self, name: str):
        self.name: Name = Name(name)
        self.phones: List[Phone] = []
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
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phone_str}{birthday_str}"


class AddressBook(UserDict):
    """Class for storing and managing records (Record). Inherits from UserDict."""

    def add_record(self, record: Record) -> None:
        name = record.name.value
        if name in self.data:
            # We allow adding a record with an existing name if we are just adding a phone
            # However, for new records, we enforce uniqueness.
            raise ValueError(f"Contact name '{name}' already exists.")
        self.data[name] = record

    def find_record_by_name(self, name: str) -> Union[Record, None]:
        return self.data.get(name)

    def find_record_by_phone(self, phone: str) -> Union[Record, None]:
        for record in self.data.values():
            if record.find_phone(phone):
                return record
        return None

    def delete(self, name: str) -> None:
        if name in self.data:
            del self.data[name]
        else:
            raise KeyError(f"Contact name '{name}' not found for deletion.")

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