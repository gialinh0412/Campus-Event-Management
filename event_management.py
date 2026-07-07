import json
import csv
import os
import tempfile
from datetime import datetime

# ==================================
# LOGIN ACCOUNT
# ==================================

ACCOUNTS = {
    "admin": {
        "password": "123456",
        "role": "Admin"
    },
    "organizer": {
        "password": "111111",
        "role": "Organizer"
    },
    "student": {
        "password": "222222",
        "role": "Student"
    }
}

# ==================================
# MODELS
# ==================================

class User:
    def __init__(self, user_id, name, role):
        self.user_id = user_id
        self.name = name
        self.role = role

class Event:
    def __init__(self, event_id, name, date, capacity):
        self.event_id = event_id
        self.name = name
        self.date = date  # datetime.date object
        self.capacity = capacity
        self.attendees = []

    @property
    def date_str(self):
        """Formatted string for display/storage purposes."""
        return self.date.strftime("%Y-%m-%d")

class Registration:
    def __init__(self, user_id, event_id):
        self.user_id = user_id
        self.event_id = event_id

# ==================================
# EVENT MANAGEMENT SYSTEM
# ==================================

class EventManagementSystem:
    def __init__(self):
        self.events = []
        self.users = []
        self.registrations = []

    def get_or_create_user(self, user_id, name, role):
        for user in self.users:
            if user.user_id == user_id:
                return user

        user = User(user_id, name, role)
        self.users.append(user)
        return user

    def add_event(self, event):
        if self.find_event(event.event_id):
            print("Event ID already exists!")
            return

        self.events.append(event)
        print("Event added successfully!")

    def format_event_row(self, event):
        status = self.get_event_status(event.date)
        return (
            f"ID: {event.event_id} | "
            f"Name: {event.name} | "
            f"Date: {event.date_str} | "
            f"Capacity: {len(event.attendees)}/{event.capacity} | "
            f"Status: {status}"
        )

    def view_events(self):
        if not self.events:
            print("No events available.")
            return

        for event in self.events:
            print(self.format_event_row(event))

    def find_event(self, event_id):

        for event in self.events:
            if event.event_id == event_id:
                return event

        return None
    
    def days_until_event(self, event_date):
        today = datetime.now().date()
        days = (event_date - today).days

        return days

    def get_event_status(self, event_date):
        days = self.days_until_event(event_date)

        if days > 0:
            return f"Starts in {days} day(s)"
        elif days == 0:
            return "Today"
        else:
            return "Event ended"

    def update_event(self, event_id, new_name):
        event = self.find_event(event_id)

        if event:
            event.name = new_name
            print("Updated!")
        else:
            print("Event not found!")

    def delete_event(self, event_id):
        event = self.find_event(event_id)

        if event:
            self.events.remove(event)

            self.registrations = [
                r for r in self.registrations if r.event_id != event_id
            ]

            print("Deleted!")
        else:
            print("Event not found!")

    def register_attendee(self, event_id, user_id):
        event = self.find_event(event_id)

        if not event:
            print("Event not found")
            return

        if user_id in event.attendees:
            print("Already registered")
            return

        if len(event.attendees) >= event.capacity:
            print("Event is full")
            return

        event.attendees.append(user_id)
        self.registrations.append(Registration(user_id, event_id))

        print("Registration successful")
        print(f"You have been registered for: {event.name}")
        print(f"Date: {event.date_str}")

        status = self.get_event_status(event.date)

        print(f"Status: {status}")

    def save_events(self):
        data = []

        for event in self.events:
            event_data = {
                "event_id": event.event_id,
                "name": event.name,
                "date": event.date_str,
                "capacity": event.capacity,
                "attendees": event.attendees
            }
            data.append(event_data)

        target_path = "events.json"
        directory = os.path.dirname(os.path.abspath(target_path)) or "."

        try:
            fd, tmp_path = tempfile.mkstemp(dir=directory, suffix=".tmp")
            with os.fdopen(fd, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)

            os.replace(tmp_path, target_path)
            print("Saved successfully!")
        except OSError as e:
            print(f"Failed to save events: {e}")

    def load_events(self):
        try:
            self.events.clear()
            self.registrations.clear()

            with open("events.json", "r", encoding="utf-8") as file:
                data = json.load(file)

            for event_data in data:
                event = Event(
                    event_data["event_id"],
                    event_data["name"],
                    datetime.strptime(event_data["date"], "%Y-%m-%d").date(),
                    event_data["capacity"]
                )
                event.attendees = event_data["attendees"]

                for attendee in event.attendees:
                    self.registrations.append(
                        Registration(attendee, event.event_id)
                    )

                self.events.append(event)

            print("Loaded successfully!")

        except FileNotFoundError:
            print("No saved data found.")
        except json.JSONDecodeError:
            print("Saved data is not valid JSON.")

    def export_report_csv(self):
        with open("report.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            writer.writerow(
                [
                    "Event ID",
                    "Event Name",
                    "Date",
                    "Capacity",
                    "Attendees"
                ]
            )

            for event in self.events:
                writer.writerow(
                    [
                        event.event_id,
                        event.name,
                        event.date,
                        event.capacity,
                        len(event.attendees)
                    ]
                )

        print("CSV report exported successfully!")
    
    def total_attendees(self):
        return sum(len(event.attendees) for event in self.events)

    def get_max_event(self):
        if not self.events:
            return None
        return max(self.events, key=lambda e: len(e.attendees))

    def get_min_event(self):
        if not self.events:
            return None
        return min(self.events, key=lambda e: len(e.attendees))

    def search_event(self, keyword):
        found = False

        for event in self.events:
            if keyword.lower() in event.name.lower():
                found = True
                print(self.format_event_row(event))

        if not found:
            print("No matching event found.")

    def view_all_attendees(self):
        if not self.events:
            print("No events available.")
            return

        for event in self.events:
            print(f"\nEvent: {event.name}")
            if event.attendees:
                for attendee in event.attendees:
                    print(f"- {attendee}")
            else:
                print("No attendees yet.")

    def view_statistics(self):
        print("\n========== STATISTICS ==========")

        total_events = len(self.events)
        total_attendees = self.total_attendees()

        print(f"Total Events       : {total_events}")
        print(f"Total Registrations: {total_attendees}")

        if total_events == 0:
            return

        if total_events == 1:
            only_event = self.events[0]
            print(f"Only Event         : {only_event.name} ({len(only_event.attendees)} attendees)")
            return

        if total_attendees == 0:
            print("No registrations yet - popularity stats unavailable.")
            return

        max_count = max(len(e.attendees) for e in self.events)
        min_count = min(len(e.attendees) for e in self.events)

        most_popular = [e for e in self.events if len(e.attendees) == max_count]
        least_popular = [e for e in self.events if len(e.attendees) == min_count]

        if len(most_popular) == len(self.events):
            print(f"All events are equally popular ({max_count} attendees each).")
            return

        tie_note = " (tie)" if len(most_popular) > 1 else ""
        names = ", ".join(e.name for e in most_popular)
        print(f"Most Popular Event{tie_note} : {names} ({max_count} attendees)")

        tie_note = " (tie)" if len(least_popular) > 1 else ""
        names = ", ".join(e.name for e in least_popular)
        print(f"Least Popular Event{tie_note}: {names} ({min_count} attendees)")

    def show_dashboard(self):
        print("\n========== ADMIN DASHBOARD ==========")

        total_events = len(self.events)
        total_registrations = self.total_attendees()
        upcoming_events = 0
        ended_events = 0
        today_events = 0

        for event in self.events:
            days = self.days_until_event(event.date)

            if days > 0:
                upcoming_events += 1
            elif days == 0:
                today_events += 1
            else:
                ended_events += 1

        print(f"Total Events            : {total_events}")
        print(f"Total Registrations     : {total_registrations}")
        print(f"Upcoming Events         : {upcoming_events}")
        print(f"Today's Events          : {today_events}")
        print(f"Ended Events            : {ended_events}")

    def view_attendees_by_event(self, event_id):
        event = self.find_event(event_id)

        if not event:
            print("Event not found!")
            return

        print(f"\nAttendees for {event.name}:")
        if event.attendees:
            for attendee in event.attendees:
                print(f"- {attendee}")
        else:
            print("No attendees yet.")

    def view_my_events(self, user_id):
        found = False

        print("\n========== MY REGISTERED EVENTS ==========")

        for event in self.events:
            if user_id in event.attendees:
                found = True

                status = self.get_event_status(event.date)

                print(f"Event ID : {event.event_id}")
                print(f"Name     : {event.name}")
                print(f"Date     : {event.date_str}")
                print(f"Status   : {status}")
                print("-" * 40)

        if not found:
            print("You have not registered for any events.")

    def view_users(self):
        print("\n========== USERS ==========")

        users = {}

        for event in self.events:
            for attendee in event.attendees:
                if attendee not in users:
                    users[attendee] = 0

                users[attendee] += 1

        if not users:
            print("No users found.")
            return
        
        print(f"{'User ID':<20}{'Registered Events':<20}")
        print("-" * 40)

        for user, count in users.items():
            print(f"{user:<20}{count}")

    def view_upcoming_events(self):
        if not self.events:
            print("No events available.")
            return
        
        print("\n========== UPCOMING EVENTS ==========")

        found = False

        for event in self.events:
            days = self.days_until_event(event.date)
            if days > 0:
                print(self.format_event_row(event))
                found = True

        if not found:
            print("No upcoming events.")

    def sort_events_by_date(self):

        if not self.events:
            print("No events available.")
            return
        
        print("\n========== EVENTS SORTED BY DATE ==========")
        sorted_events = sorted(self.events, key=lambda event: event.date)

        for event in sorted_events:
            print(self.format_event_row(event))

# ==================================
# MENU HELPERS
# ==================================

def input_event_id():
    try:
        return int(input("Event ID: "))
    except ValueError:
        print("Invalid Event ID!")
        return None


def add_event_menu(ems):
    event_id = input_event_id()

    if event_id is None:
        return
    
    if ems.find_event(event_id):
        print("Event ID already exists!")
        return

    name = input("Event Name: ")

    if name.strip() == "":
        print("Event name cannot be empty.")
        return

    date_input = input("Date (YYYY-MM-DD): ")

    try:
        date = datetime.strptime(date_input, "%Y-%m-%d").date()
    except ValueError:
        print("Invalid date! Please enter a valid date in YYYY-MM-DD format.")
        return

    try:
        capacity = int(input("Capacity: "))
    except ValueError:
        print("Invalid number!")
        return

    if capacity <= 0:
        print("Capacity must be greater than 0.")
        return

    event = Event(event_id, name, date, capacity)
    ems.add_event(event)
    ems.save_events()


def admin_menu(ems):
    while True:
        print("\n===== ADMIN MENU =====")
        print("1. Add Event")
        print("2. View Events")
        print("3. Update Event")
        print("4. Delete Event")
        print("5. View All Attendees")
        print("6. Save Events")
        print("7. Load Events")
        print("8. Export CSV")
        print("9. View Statistics")
        print("10. View Users")
        print("11. Upcoming Events")
        print("12. Sort Events by Date")
        print("13. Back")

        choice = input("Enter your choice: ")

        if choice == "1":
            add_event_menu(ems)
        elif choice == "2":
            ems.view_events()
        elif choice == "3":
            event_id = input_event_id()
            if event_id is None:
                continue

            new_name = input("New Event Name: ")
            if new_name.strip() == "":
                print("Event name cannot be empty.")
                continue

            ems.update_event(event_id, new_name)
            ems.save_events()
        elif choice == "4":
            event_id = input_event_id()
            if event_id is None:
                continue

            ems.delete_event(event_id)
            ems.save_events()
        elif choice == "5":
            ems.view_all_attendees()
        elif choice == "6":
            ems.save_events()
        elif choice == "7":
            ems.load_events()
        elif choice == "8":
            ems.export_report_csv()
        elif choice == "9":
            ems.view_statistics()
        elif choice == "10":
            ems.view_users()
        elif choice == "11":
            ems.view_upcoming_events()
        elif choice == "12":
            ems.sort_events_by_date()
        elif choice == "13":
            break
        else:
            print("Invalid choice!")


def organizer_menu(ems):
    while True:
        print("\n===== EVENT ORGANIZER MENU =====")
        print("1. View Events")
        print("2. Register Attendee")
        print("3. View Attendees By Event")
        print("4. Save Events")
        print("5. Back")

        choice = input("Enter your choice: ")

        if choice == "1":
            ems.view_events()
        elif choice == "2":
            event_id = input_event_id()
            if event_id is None:
                continue

            user_id = input("User ID: ")
            ems.register_attendee(event_id, user_id)
        elif choice == "3":
            event_id = input_event_id()
            if event_id is None:
                continue

            ems.view_attendees_by_event(event_id)
        elif choice == "4":
            ems.save_events()
        elif choice == "5":
            break
        else:
            print("Invalid choice!")


def student_menu(ems, user):
    while True:
        print("\n===== STUDENT / VISITOR MENU =====")
        print(f"Logged in as: {user.user_id}")
        print("1. Search Event")
        print("2. Register Event")
        print("3. View My Registered Events")
        print("4. Back")

        choice = input("Enter your choice: ")

        if choice == "1":
            keyword = input("Keyword: ")
            ems.search_event(keyword)
        elif choice == "2":
            event_id = input_event_id()
            if event_id is None:
                continue

            # Students can only register themselves, tied to their login.
            ems.register_attendee(event_id, user.user_id)
        elif choice == "3":
            ems.view_my_events(user.user_id)
        elif choice == "4":
            break
        else:
            print("Invalid choice!")

# ==================================
# MAIN PROGRAM
# ==================================

def login(ems):
    print("\n========== LOGIN ==========")

    username = input("Username: ")
    password = input("Password: ")

    if username not in ACCOUNTS:
        print("Username does not exist!")
        return None
    
    if password != ACCOUNTS[username]["password"]:
        print("Incorrect password!")
        return None
    
    role = ACCOUNTS[username]["role"]
    print(f"Welcome {username}!")

    # Ties the authenticated login to a real User object instead of
    # just handing back a bare role string.
    return ems.get_or_create_user(username, username, role)

def main():
    ems = EventManagementSystem()
    ems.load_events()

    while True:
       
        user = login(ems)

        if user is None:
            continue

        if user.role == "Admin":
           ems.show_dashboard()
           admin_menu(ems)

        elif user.role == "Organizer":
           organizer_menu(ems)

        elif user.role == "Student":
            student_menu(ems, user)

        else:
           print("Login failed.")

        print("\n1. Login again")
        print("2. Exit")

        choice = input("Choose: ")

        if choice == "2":
            print("Goodbye!")
            break
           
# ==================================
# ENTRY POINT
# ==================================

if __name__ == "__main__":
    main()
