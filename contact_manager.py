import json
import os
import logging

CONTACTS_FILE = "contacts.json"
LOG_FILE = "contacts.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


class ContactAlreadyExistsError(Exception):
    pass


class ContactNotFoundError(Exception):
    pass


class InvalidInputError(Exception):
    pass


class ContactFileError(Exception):
    """Raised when the contacts file is missing, unreadable, or corrupted."""
    pass


def load_contacts():
    if not os.path.exists(CONTACTS_FILE):
        logging.warning("Contacts file not found. Starting with empty contacts list.")
        return {}

    file = None
    contacts = {}

    try:
        file = open(CONTACTS_FILE, "r")
        contacts = json.load(file)
    except json.JSONDecodeError as e:
        logging.error(f"Corrupted JSON file: {e}")
        print("⚠️  Contacts file is corrupted. Starting with empty contacts list.")
        raise ContactFileError("Contacts file was corrupted and has been reset for this session.") from e
    except OSError as e:
        logging.error(f"Could not open contacts file: {e}")
        print("❌ Could not read contacts file.")
        raise ContactFileError("Contacts file could not be opened.") from e
    else:
        logging.info(f"Contacts loaded successfully ({len(contacts)} contacts).")
    finally:
        if file:
            file.close()
            logging.debug("Contacts file closed after loading.")

    return contacts


def save_contacts(contacts):
    try:
        with open(CONTACTS_FILE, "w") as file:
            json.dump(contacts, file, indent=4)
    except OSError as e:
        logging.error(f"Failed to save contacts: {e}")
        print("❌ Could not save contacts. Your changes may not be stored.")
    else:
        logging.info(f"Contacts saved successfully ({len(contacts)} contacts).")


def add_contact(contacts):
    try:
        name = input("Enter Name: ").strip()
        if not name:
            raise InvalidInputError("Name cannot be empty.")

        phone = input("Enter Phone Number: ").strip()
        if not phone:
            raise InvalidInputError("Phone number cannot be empty.")

        email = input("Enter Email: ").strip()

        if name.lower() in [n.lower() for n in contacts]:
            raise ContactAlreadyExistsError(f"A contact named '{name}' already exists.")

        contacts[name] = {"phone": phone, "email": email}
        save_contacts(contacts)
        logging.info(f"New contact added: '{name}'")
        print(f"✅ Contact '{name}' added successfully.")

    except InvalidInputError as e:
        logging.warning(f"Invalid input while adding contact: {e}")
        print(f"❌ {e}")

    except ContactAlreadyExistsError as e:
        logging.warning(str(e))
        print(f"⚠️  {e}")


def search_contact(contacts):
    try:
        query = input("Enter name, phone, or email to search: ").strip()
        if not query:
            raise InvalidInputError("Search query cannot be empty.")

        query_lower = query.lower()
        results = [
            (name, details) for name, details in contacts.items()
            if query_lower in name.lower()
            or query_lower in details["phone"]
            or query_lower in details["email"].lower()
        ]

        if not results:
            raise ContactNotFoundError(f"No contacts found matching '{query}'.")

        logging.info(f"Search for '{query}' returned {len(results)} result(s).")
        print(f"\n🔍 Found {len(results)} result(s):")
        print("-" * 35)
        for name, details in results:
            print(f"Name  : {name}")
            print(f"Phone : {details['phone']}")
            print(f"Email : {details['email']}")
            print("-" * 35)

    except InvalidInputError as e:
        logging.warning(f"Invalid search input: {e}")
        print(f"❌ {e}")

    except ContactNotFoundError as e:
        logging.info(str(e))
        print(f"⚠️  {e}")


def display_all_contacts(contacts):
    try:
        if not contacts:
            raise ContactNotFoundError("No contacts saved yet.")

        print(f"\n📋 All Contacts ({len(contacts)} total)")
        print("=" * 35)
        for name, details in contacts.items():
            print(f"Name  : {name}")
            print(f"Phone : {details['phone']}")
            print(f"Email : {details['email']}")
            print("-" * 35)

    except ContactNotFoundError as e:
        logging.info(f"Display requested but no contacts exist: {e}")
        print(f"⚠️  {e}")

    else:
        logging.info(f"Displaying all {len(contacts)} contacts.")


def main():
    logging.info("===== Contact Management System Started =====")
    print("📱 Contact Management System")

    try:
        contacts = load_contacts()
    except ContactFileError as e:
        logging.error(f"Startup file error: {e}")
        print(f"⚠️  {e} Continuing with an empty contact list.")
        contacts = {}

    while True:
        try:
            print("\n===== MENU =====")
            print("1. Add Contact")
            print("2. Search Contact")
            print("3. View All Contacts")
            print("4. Exit")
            choice = input("Enter your choice (1-4): ").strip()

            if choice == "1":
                add_contact(contacts)
            elif choice == "2":
                search_contact(contacts)
            elif choice == "3":
                display_all_contacts(contacts)
            elif choice == "4":
                logging.info("===== Contact Management System Exited =====")
                print("✅ Goodbye!")
                break
            else:
                logging.warning(f"Invalid menu choice entered: '{choice}'")
                print("❌ Invalid choice! Enter 1-4.")

        except KeyboardInterrupt:
            logging.warning("Program interrupted by user (KeyboardInterrupt).")
            print("\n\n⚠️  Interrupted. Goodbye!")
            break

        except Exception as e:
            # Last-resort safety net so an unexpected error never crashes the CLI.
            logging.error(f"Unexpected error in main loop: {e}")
            print(f"❌ Something went wrong: {e}")
            print("The program will continue running.")


if __name__ == "__main__":
    main()
      
