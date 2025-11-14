# Personal Assistant (CLI Address Book)

The **Personal Assistant** is a command-line application designed to help you organize and manage your contacts and notes. It stores all user data on disk, ensuring nothing is lost between sessions. The assistant provides easy tools for adding, editing, searching, and removing both contacts and notes, as well as validating user input to prevent mistakes.

## Key Features:
### Contact management:

- Add new contacts including names, phone numbers, email addresses and birthdays.
- Persistent storage of contacts and notes on disk.
- User-friendly command-line interface.
- Input validation for phone numbers and email addresses during creation or updates.
- Show contacts whose birthdays occur within a specified number of days from today
- Comprehensive commands for managing contacts and notes.

### Note management:
- Add text notes.
- Search notes by keywords.
- Edit and delete notes.
- View all notes in the notebook.

### Persistent Data Storage:
- All contacts and notes are automatically saved on the user’s disk.
- The assistant can be restarted at any time without losing data.


---

## Requirements

- Python 3.10+ (or the version required by your project)
- `pip` (comes with most Python installations)

---

## Installation

### 1. Clone the repository

If you haven’t already:

```bash
git clone https://github.com/neo-team-26/assistant
cd assistant
```

### 2. Create a virtual environment

Create a virtual environment to manage dependencies:

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

- On Windows:
  ```bash
  .venv\Scripts\activate
  ```
- On macOS/Linux:
  ```bash
  source .venv/bin/activate
  ```

### 4. Command List

| Command            | Arguments / Format           | Description                                                                 | Example                                        |
| ------------------ | ---------------------------- | --------------------------------------------------------------------------- | ---------------------------------------------- |
| **add**            | `<name> <phone>`             | Adds a new contact with the specified name and phone number.                | `add John +380501234567`                       |
| **change**         | `<name> <new_phone>`         | Updates the phone number of an existing contact.                            | `change John +380509998877`                    |
| **delete**         | `<name>` or `<name> <phone>` | Deletes a contact or removes a specific phone number.                       | `delete John` / `delete John +380501234567`    |
| **phone**          | `<name>`                     | Displays all phone numbers associated with the contact.                     | `phone John`                                   |
| **all**            | —                            | Shows all contacts stored in the address book.                              | `all`                                          |
| **add-birthday**   | `<name> <DD.MM.YYYY>`        | Adds a birthday to a contact (creates the contact if it does not exist).    | `add-birthday John 25.12.1990`                 |
| **show-birthday**  | `<name>`                     | Displays the birthday of the specified contact.                             | `show-birthday John`                           |
| **birthdays**      | `<days>`                     | Shows upcoming birthdays within the next `<days>` days, grouped by weekday. | `birthdays 7`                                  |
| **add-email**      | `<name> <email>`             | Adds an email address to a contact.                                         | `add-email John john@example.com`              |
| **remove-email**   | `<name> <email>`             | Removes the specified email address from a contact.                         | `remove-email John john@example.com`           |
| **change-email**   | `<name> <new_email>`         | Replaces the contact’s email with a new one.                                | `change-email John new@example.com`            |
| **add-address**    | `<name> <address>`           | Adds a physical address to a contact.                                       | `add-address John "Kyiv, Main St 10"`          |
| **remove-address** | `<name>`                     | Removes the contact’s physical address.                                     | `remove-address John`                          |
| **change-address** | `<name> <new_address>`       | Updates the physical address of the contact.                                | `change-address John "Lviv, Freedom Sq 2"`     |
| **add-note**       | `<title> <text>`             | Adds a note with a title and text.                                          | `add-note Shopping "Buy apples and milk"`      |
| **edit-note**      | `<title> <new_text>`         | Edits an existing note.                                                     | `edit-note Shopping "Buy apples, milk, bread"` |
| **delete-note**    | `<title>`                    | Deletes the note with the specified title.                                  | `delete-note Shopping`                         |
| **all-notes**      | —                            | Displays all notes in the notebook.                                         | `all-notes`                                    |
| **find-notes**     | `<keyword>`                  | Lists all notes that contain the given keyword.                             | `find-notes milk`                              |
| **get-note**       | `<title>`                    | Shows the full content of the specified note.                               | `get-note Shopping`                            |
| **help**           | —                            | Displays help information for all commands.                                 | `help`                                         |
