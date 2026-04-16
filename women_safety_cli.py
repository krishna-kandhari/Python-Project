# This is a simple Python script for a Women Safety Terminal.
# We import tools that help us do things like using the internet, pausing the program, and saving files.  # noqa: E501
import os
import sys
import time
import json
import getpass
import hashlib
import requests
import urllib.parse
import webbrowser
import threading

# ==========================================
# STEP 1: GLOBAL VARIABLES (OUR SAVED STATE)
# ==========================================
# These variables remember what the app is currently doing

# User Data
current_username = ""
current_full_name = "User"
current_emergency_pin = "0000"
current_contacts = []

# App Status
is_siren_playing = False
is_timer_running = False
timer_seconds_left = 0
is_timer_periodic = False
timer_original_minutes = 0

# Database rule: We will save everyone's accounts into this file
USERS_FILE = "users.json"


# ==========================================
# STEP 2: HELPER FUNCTIONS
# ==========================================

def clear_screen():
    """
    This clears the messy text out of the terminal window so it looks neat.
    If you are on Windows ('nt'), type 'cls'. If Mac/Linux, type 'clear'.
    """
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


def scramble_password(password):
    """
    We don't want hackers to read passwords, so we scramble (hash) them
    into random-looking text before saving them.
    """
    return hashlib.sha256(password.encode()).hexdigest()


def get_live_location():
    """
    This function talks to the internet to find out approximately where you are based on your IP address.  # noqa: E501
    """
    try:
        # We ask 'ip-api.com' for our location
        response = requests.get("http://ip-api.com/json/").json()

        # If it worked, we extract the coordinates and city
        lat = response.get("lat")
        lon = response.get("lon")
        city = response.get("city")

        # Then we make a Google Maps link!
        google_maps_link = f"https://www.google.com/maps?q={lat},{lon}"

        return True, f"{city} | Map: {google_maps_link}"
    except Exception:
        # If the internet is broken, we catch the error so the app doesn't crash  # noqa: E501
        return False, "Could not find your location. Please check internet connection."  # noqa: E501


def trigger_whatsapp_sos(message_to_send):
    """
    This loops through your contacts and automatically triggers WhatsApp on your computer to send them a message.  # noqa: E501
    """
    if len(current_contacts) == 0:
        print("Error: No emergency contacts found!")
        return

    success_count = 0
    print(f"Sending WhatsApp message to {len(current_contacts)} people...")

    # Loop through each friend in your contacts list
    for person in current_contacts:
        phone_number = person["phone"]

        # Don't try to send a WhatsApp to 911/112 (it will break the application)  # noqa: E501
        if len(phone_number) <= 4:
            continue

        try:
            # We fix the message formatting so it works as a web link
            safe_text = urllib.parse.quote(message_to_send)

            # This special link tells the computer to open the WhatsApp app
            whatsapp_link = f"whatsapp://send?phone={phone_number}&text={safe_text}"  # noqa: E501
            webbrowser.open(whatsapp_link)

            success_count += 1
            # Pause for 3 seconds so the app has time to load before the next person  # noqa: E501
            time.sleep(3)
        except Exception:
            pass

    print(f"Successfully opened WhatsApp for {success_count} contacts.")


# ==========================================
# STEP 3: BACKGROUND TIMERS & SIRENS
# ==========================================

def background_timer_loop():
    """
    This is the countdown loop that runs totally invisibly in the background.
    """
    global is_timer_running, timer_seconds_left

    # Keep looping as long as the timer is running and time is left
    while is_timer_running and timer_seconds_left > 0:
        time.sleep(1)  # Wait exactly 1 second
        timer_seconds_left = timer_seconds_left - 1  # Subtract 1 second

        # If there are exactly 60 seconds left, play a warning beep!
        if timer_seconds_left == 60:
            os.system("say 'Warning. Safety timer expiring in 60 seconds.'")
            print("\a", end="\r")  # Terminal beep

    # If the loop finishes naturally (because time ran out!)
    if is_timer_running and timer_seconds_left <= 0:
        is_timer_running = False

        # Uh oh! Time ran out. Trigger the SOS immediately.
        print("\n\n!!! TIMER EXPIRED - SENDING AUTOMATIC SOS !!!\n\n")

        # Get location and send the text
        success, loc_text = get_live_location()
        sos_message = "🚨 EMERGENCY 🚨\nMy safety timer expired and I did not check in! I need help.\n" + loc_text  # noqa: E501
        trigger_whatsapp_sos(sos_message)


def background_siren_loop():
    """ Keeps blaring the audio horn in the background until you turn it off """  # noqa: E501
    while is_siren_playing:
        # 'afplay' plays a sound effect on macOS
        os.system("afplay /System/Library/Sounds/Submarine.aiff")


# ==========================================
# STEP 4: DATABASE / SAVING TO FILE
# ==========================================

def save_database(all_users_dictionary):
    """ Overwrites the text file with our new data so it saves permanently """
    with open(USERS_FILE, "w") as file:
        json.dump(all_users_dictionary, file, indent=4)


def load_database():
    """ Reads the permanent text file back into Python """
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as file:
            return json.load(file)
    else:
        # If the file doesn't exist yet, return an empty dictionary
        return {}


# ==========================================
# STEP 5: AUTHENTICATION MENU (LOGIN/SIGNUP)
# ==========================================

def authentication_screen():
    """ This is the very first screen the user sees when they open the app """
    global current_username, current_full_name, current_emergency_pin, current_contacts  # noqa: E501

    while True:
        clear_screen()
        print("====================================")
        print("    🔐 WOMEN SAFETY APP LOGIN")
        print("====================================")
        print("1. Login")
        print("2. Sign Up")
        print("3. Exit\n")

        choice = input("Select an option (1-3): ")

        # If they chose to Login
        if choice == "1":
            typed_user = input("Username: ")
            typed_pass = getpass.getpass("Password: ")

            all_users = load_database()

            # Check if username exists and if the scrambled password matches
            if typed_user in all_users and all_users[typed_user]["password"] == scramble_password(typed_pass):  # noqa: E501
                # Success! Set our global variables to remember who logged in
                current_username = typed_user
                current_full_name = all_users[typed_user]["full_name"]
                current_emergency_pin = all_users[typed_user]["pin"]
                current_contacts = all_users[typed_user]["contacts"]

                print("Login successful!")
                time.sleep(1)
                break  # Exit the login loop and enter the main app!
            else:
                print("Error: Invalid username or password.")
                time.sleep(1.5)

        # If they chose to create a new account
        elif choice == "2":
            full_name = input("Full Name: ")
            new_user = input("Choose a Username: ")
            new_pass = getpass.getpass("Choose a Password: ")
            pin = input("Set a 4-digit Emergency PIN to stop the timer: ")

            all_users = load_database()
            if new_user in all_users:
                print("Error: That username is already taken.")
                time.sleep(1.5)
                continue

            # Create the data for the new user, pre-loaded with police numbers
            initial_contacts = [
                {"name": "National Emergency", "phone": "112"},
                {"name": "Women Helpline", "phone": "1091"},
                {"name": "Police", "phone": "100"}
            ]
            
            print("\nPlease add at least one personal emergency contact.")
            c_name = input("Emergency Contact Name: ")
            c_phone = input("Phone Number (10 digits): ")
            
            c_phone = c_phone.strip()
            if len(c_phone) == 10 and c_phone.isdigit():
                c_phone = "+91" + c_phone
                
            if c_name and c_phone:
                initial_contacts.append({"name": c_name, "phone": c_phone})
                
            all_users[new_user] = {
                "full_name": full_name,
                "password": scramble_password(new_pass),
                "pin": pin,
                "contacts": initial_contacts
            }
            save_database(all_users)

            print("Account created successfully! You can now log in.")
            time.sleep(2)

        # If they chose to quit
        elif choice == "3":
            sys.exit()


# ==========================================
# STEP 6: THE MAIN APP MENU
# ==========================================

def app_main_menu():
    """ This is the core hub of the application after you log in """
    global is_siren_playing, is_timer_running, timer_seconds_left, is_timer_periodic, timer_original_minutes  # noqa: E501

    while True:
        clear_screen()
        print("==================================================")
        print("           🚨 WOMEN SAFETY TERMINAL 🚨          ")
        print(f"               Welcome, {current_full_name}     ")
        print("==================================================")

        # Display the current status of sirens and timers
        print("\nCurrent Status:")
        if is_siren_playing:
            print("🔊 SIREN: ON (Playing)")
        else:
            print("🔊 SIREN: OFF")

        if is_timer_running:
            # Do math to figure out how many minutes and seconds are left
            mins_left = timer_seconds_left // 60
            secs_left = timer_seconds_left % 60
            print(f"⏱️  TIMER: RUNNING ({mins_left} mins and {secs_left} secs left)")  # noqa: E501
        else:
            print("⏱️  TIMER: OFF")

        print("--------------------------------------------------\n")
        print("Choose an Action:")
        print("1. 🚨 TRIGGER SOS (Send Location)")
        print("2. 🔊 TOGGLE SIREN")
        print("3. 📞 FAKE CALL")
        print("4. ⏱️  SAFETY TIMER (Check-in)")
        print("5. 👥 MANAGE CONTACTS")
        print("6. ❌ EXIT\n")

        choice = input("Select an option (1-6): ")

        # Feature 1: The SOS Button
        if choice == "1":
            print("\nFetching your location...")
            success, loc_text = get_live_location()
            print(loc_text)

            message = "🚨 EMERGENCY 🚨\nI am in danger and need help immediately.\n" + loc_text  # noqa: E501
            trigger_whatsapp_sos(message)
            input("\nPress Enter to continue...")

        # Feature 2: The Loud Siren
        elif choice == "2":
            if is_siren_playing:
                is_siren_playing = False  # Turn it off
                print("\nSiren turned off.")
            else:
                is_siren_playing = True  # Turn it on
                # Start the background siren worker
                threading.Thread(target=background_siren_loop, daemon=True).start()  # noqa: E501
                print("\nSiren TURNED ON!")
            time.sleep(1.5)

        # Feature 3: The Fake Call
        elif choice == "3":
            clear_screen()
            print("=====================================")
            print("         📞 INCOMING CALL...        ")
            print("             Dad (Home)             ")
            print("=====================================")

            # Use computer voice to pretend it's ringing
            os.system("say -v Alex 'Ring... Ring... Ring... Incoming call from Dad'")  # noqa: E501
            input("Press Enter to hang up...")

        # Feature 4: Safety Timer / Journey Mode
        elif choice == "4":
            # If it is already running, ask for the secret PIN to turn it off
            if is_timer_running:
                typed_pin = input("\nTimer is running. Enter your PIN to disarm or check-in: ")  # noqa: E501
                if typed_pin == current_emergency_pin:
                    if is_timer_periodic:
                        # Reset the time back to full
                        timer_seconds_left = timer_original_minutes * 60
                        print("Checked in! Timer reset to keep tracking you.")
                    else:
                        is_timer_running = False  # Turn it off completely
                        print("Timer stopped.")
                else:
                    print("Incorrect PIN!")
                time.sleep(1.5)

            # If no timer is running, let them start one
            else:
                clear_screen()
                print("====== 🛡️ JOURNEY MODE 🛡️  ======")
                print("1. Single Countdown Timer")
                print("2. Periodic Check-In (Makes you type your PIN every X minutes)")  # noqa: E501
                mode = input("Select timer mode (1 or 2): ")

                mins_str = input("Enter duration in minutes (e.g., 30): ")
                try:
                    timer_original_minutes = int(mins_str)
                except Exception:
                    print("Invalid number.")
                    time.sleep(1)
                    continue

                notify = input("Notify your contacts you are starting a trip? (y/n): ")  # noqa: E501

                # Setup the state variables
                is_timer_running = True
                timer_seconds_left = timer_original_minutes * 60

                if mode == "2":
                    is_timer_periodic = True
                else:
                    is_timer_periodic = False

                # Broadcast departure
                if notify.lower() == "y":
                    print("\nFetching your location to broadcast departure...")
                    success, loc_text = get_live_location()

                    msg = f"🛡️ JOURNEY INFO 🛡️\nI am starting a trip. If I do not check-in in {timer_original_minutes} mins, you will get an SOS.\n" + loc_text  # noqa: E501
                    trigger_whatsapp_sos(msg)

                # Start the background loop worker
                # (daemon=True means it silently dies if we close the main app)
                threading.Thread(target=background_timer_loop, daemon=True).start()  # noqa: E501

                print(f"\nTimer started successfully for {timer_original_minutes} minutes!")  # noqa: E501
                time.sleep(2)

        # Feature 5: Contacts Menu
        elif choice == "5":
            while True:
                clear_screen()
                print("--- Your Emergency Contacts ---")

                # Show all people on your list
                for i, person in enumerate(current_contacts):
                    print(f"ID {i+1} | Name: {person['name']} | Phone: {person['phone']}")  # noqa: E501

                print("\nOptions:")
                print("1. Add Contact")
                print("2. Delete Contact")
                print("3. Back to Main Menu")

                sub_choice = input("Select an option (1-3): ")

                if sub_choice == "1":
                    c_name = input("Enter Contact Name: ")
                    c_phone = input("Phone Number (10 digits): ")

                    # Clean up the phone number and add Indian country code if needed  # noqa: E501
                    c_phone = c_phone.strip()
                    if len(c_phone) == 10 and c_phone.isdigit():
                        c_phone = "+91" + c_phone

                    # Add them to our global list
                    current_contacts.append({"name": c_name, "phone": c_phone})

                    # Update the database text file permanently
                    all_users = load_database()
                    all_users[current_username]["contacts"] = current_contacts
                    save_database(all_users)

                    print("Contact added successfully!")
                    time.sleep(1)

                elif sub_choice == "2" and len(current_contacts) > 0:
                    try:
                        idx_str = input("Enter Contact ID to delete: ")
                        idx = int(idx_str) - 1  # Computer lists start at 0
                        removed = current_contacts.pop(idx)

                        # Save the updated list
                        all_users = load_database()
                        all_users[current_username]["contacts"] = current_contacts  # noqa: E501
                        save_database(all_users)

                        print(f"Deleted {removed['name']}.")
                    except Exception:
                        print("Invalid ID.")
                    time.sleep(1)

                elif sub_choice == "3":
                    break  # Go back

        # Exit App
        elif choice == "6":
            print("\nExiting. Stay safe!")
            is_timer_running = False
            is_siren_playing = False
            sys.exit()


# Run the app if this file is double-clicked or run in terminal
if __name__ == "__main__":
    # Make sure we save the database file exactly in the folder this script runs from  # noqa: E501
    script_directory = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_directory)

    # Catch CTRL+C cleanly
    try:
        authentication_screen()
        app_main_menu()
    except KeyboardInterrupt:
        print("\n\nForce quitting. Stay safe!")
        is_timer_running = False
        is_siren_playing = False
        sys.exit()
