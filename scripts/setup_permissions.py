#!/usr/bin/env python3
"""
Request Calendar and Reminders access for the Apple EventKit Host app.

Run it through the host so macOS attributes the request to the host:

    open -g "$HOME/Applications/Apple EventKit Host.app" --args \\
        /opt/homebrew/bin/uv --directory /Users/laurens/.scripts/apple-eventkit-mcp \\
        run python /Users/laurens/.scripts/apple-eventkit-mcp/scripts/setup_permissions.py

Run directly from a terminal, it requests access for that terminal app instead.
"""

import sys
import time
import threading

try:
    import EventKit
except ImportError:
    print("Error: pyobjc-framework-EventKit is required.")
    print("Install it with: pip install pyobjc-framework-EventKit")
    sys.exit(1)


def get_status_name(status: int) -> str:
    """Convert authorization status to readable name."""
    status_map = {
        0: "Not Determined",
        1: "Restricted",
        2: "Denied",
        3: "Authorized",
        4: "Write Only (macOS 14+)",
    }
    return status_map.get(status, f"Unknown ({status})")


def check_current_status():
    """Display current permission status."""
    cal_status = EventKit.EKEventStore.authorizationStatusForEntityType_(
        EventKit.EKEntityTypeEvent
    )
    rem_status = EventKit.EKEventStore.authorizationStatusForEntityType_(
        EventKit.EKEntityTypeReminder
    )

    print("\n=== Current Permission Status ===")
    print(f"Calendar:  {get_status_name(cal_status)}")
    print(f"Reminders: {get_status_name(rem_status)}")

    return cal_status, rem_status


def request_permissions():
    """Request Calendar and Reminders permissions."""
    store = EventKit.EKEventStore.alloc().init()

    cal_status, rem_status = check_current_status()

    # Track results
    results = {"calendar": None, "reminders": None}
    completed = threading.Event()
    pending = {"count": 0}

    def calendar_callback(granted, error):
        results["calendar"] = granted
        if error:
            print(f"Calendar error: {error}")
        pending["count"] -= 1
        if pending["count"] == 0:
            completed.set()

    def reminders_callback(granted, error):
        results["reminders"] = granted
        if error:
            print(f"Reminders error: {error}")
        pending["count"] -= 1
        if pending["count"] == 0:
            completed.set()

    # Request Calendar permission if needed
    if cal_status == 0:  # Not Determined
        print("\nRequesting Calendar access...")
        print(">>> A system dialog should appear. Please click 'OK' to grant access.")
        pending["count"] += 1
        store.requestFullAccessToEventsWithCompletion_(calendar_callback)
    elif cal_status == 3:  # Authorized
        print("\nCalendar: Already authorized")
        results["calendar"] = True
    else:
        print(f"\nCalendar: {get_status_name(cal_status)}")
        print("  Enable Apple EventKit Host in: System Settings > Privacy & Security > Calendars")
        results["calendar"] = False

    # Request Reminders permission if needed
    if rem_status == 0:  # Not Determined
        print("\nRequesting Reminders access...")
        print(">>> A system dialog should appear. Please click 'OK' to grant access.")
        pending["count"] += 1
        store.requestFullAccessToRemindersWithCompletion_(reminders_callback)
    elif rem_status == 3:  # Authorized
        print("\nReminders: Already authorized")
        results["reminders"] = True
    else:
        print(f"\nReminders: {get_status_name(rem_status)}")
        print("  Enable Apple EventKit Host in: System Settings > Privacy & Security > Reminders")
        results["reminders"] = False

    # Wait for callbacks if we requested any
    if pending["count"] > 0:
        print("\nWaiting for permission dialogs...")
        print("(This may take up to 60 seconds if dialogs don't appear)")

        # Wait for completion or timeout
        completed.wait(timeout=60)

        # Give a moment for the system to update
        time.sleep(1)

    return results


def main():
    print("=" * 60)
    print("Apple EventKit MCP Server - Permission Setup")
    print("=" * 60)
    print()
    print("This script will request Calendar and Reminders permissions.")
    print("You should see system dialogs asking for permission.")
    print()

    results = request_permissions()

    # Check final status
    print("\n" + "=" * 60)
    final_cal, final_rem = check_current_status()
    print("=" * 60)

    if final_cal == 3 and final_rem == 3:
        print("\n✓ SUCCESS: All permissions granted!")
    else:
        print("\n⚠ Some permissions are missing.")
        print("\nEnable Apple EventKit Host in System Settings > Privacy & Security >")
        print("Calendars and Reminders, or remove its entry there and run this again.")


if __name__ == "__main__":
    main()
