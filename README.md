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

## Interactive prompts and cancellation

- Some commands are interactive (for example `create-contact-wizard` or when multiple
  contacts match a name and the program asks you to pick a Contact ID).
- Pressing `Ctrl+C` during an interactive prompt will cancel the current operation
  gracefully and return you to the main prompt (no traceback).

## Notes

- The CLI stores data in `addressbook.pkl` and `notebook.pkl` in the project folder.
- Command names and behaviors may be updated; use `help` for the latest command list.


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

| Command            | Arguments / Format                       | Description                                                                 | Example                                            |
| ------------------ | ---------------------------------------- | --------------------------------------------------------------------------- | -------------------------------------------------- |
| **create-contact** | `<name> <phone>`                         | Create a new contact (requires a phone).                                    | `create-contact John 0123456789`                   |
| **create-contact-wizard** | (interactive)                       | Interactive flow to create a contact with multiple fields.                  | `create-contact-wizard`                              |
| **show-phone**     | `<name>`                                 | If one contact matches: shows the contact's phone(s). If multiple matches: shows name, ID, phones and other details (emails, addresses, birthday). | `show-phone John`                                   |
| **add-phone**      | `<name> <phone>`                         | Adds a phone number to the specified contact (will prompt if multiple contacts with that name). | `add-phone John 0987654321`                        |
| **update-phone**   | `<name> <old_phone> <new_phone>`         | Replace an existing phone for a contact.                                     | `update-phone John 0123456789 0987654321`         |
| **delete-phone**   | `<name> <phone>`                         | Delete a phone from a contact.                                               | `delete-phone John 0123456789`                    |
| **all**            | —                                        | Show all contacts.                                                            | `all`                                              |
| **add-birthday**   | `<name> <DD.MM.YYYY>`                    | Adds a birthday to a contact (creates contact if missing).                   | `add-birthday John 25.12.1990`                    |
| **show-birthday**  | `<name>`                                 | Shows birthday for the contact (prompts if multiple matches).               | `show-birthday John`                               |
| **birthdays**      | `<days>`                                 | Lists upcoming birthdays within next `<days>` days.                         | `birthdays 7`                                      |
| **add-email**      | `<name> <email>`                         | Adds an email address to a contact.                                          | `add-email John john@example.com`                 |
| **remove-email**   | `<name> <email>`                         | Removes an email from a contact.                                             | `remove-email John john@example.com`              |
| **change-email**   | `<name> <old_email> <new_email>`         | Update an email for a contact.                                               | `change-email John old@example.com new@example.com`|
| **add-address**    | `<name> <address>`                       | Adds a physical address to a contact.                                        | `add-address John "Kyiv, Main St 10"`            |
| **remove-address** | `<name> <address>`                       | Removes the specified address from a contact.                                | `remove-address John "Kyiv, Main St 10"`         |
| **change-address** | `<name> <old_address> <new_address>`     | Change an address for a contact.                                              | `change-address John "Old" "New"`             |
| **add-note**       | `<title> <text> [#tags]`                 | Add a note with optional tags.                                                | `add-note Shopping "Buy apples" #groceries`     |
| **edit-note**      | `<title> <text>`                         | Edit an existing note.                                                        | `edit-note Shopping "Buy apples and milk"`      |
| **delete-note**    | `<title>`                                | Delete a note.                                                                | `delete-note Shopping`                            |
| **all-notes**      | —                                        | List all notes.                                                               | `all-notes`                                        |
| **find-notes**     | `<filters>`                              | Search notes by keywords and tags (see `help find-notes`).                   | `find-notes report +financial -draft #urgent`    |
| **show-note**      | `<title>`                                | Show a note's content.                                                        | `show-note Shopping`                              |
| **help**           | —                                        | Show detailed help for commands.                                              | `help`                                             |
