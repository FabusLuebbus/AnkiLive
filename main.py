"""
AnkiLive - A tool for creating Anki flashcards from lecture slides.

This is the main entry point for the application.
"""

import logging
import sys
from pynput import keyboard
from src.orchestrator import Orchestrator
from src.ui import get_deck_name

def get_deck_name_fallback():
    """Simple fallback method to get deck name using console input."""
    print("Please enter a name for your Anki deck (or press Enter for default 'AnkiLive'):")
    try:
        deck_name = input("> ").strip()
        if not deck_name:
            deck_name = "AnkiLive"
        return deck_name
    except (KeyboardInterrupt, EOFError):
        print("\nUsing default deck name: AnkiLive")
        return "AnkiLive"


def main():
    """Run the AnkiLive application."""
    # Configure logging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Ask for the deck name at startup
    print("Welcome to AnkiLive!")
    
    # Try to use the GUI dialog first
    try:
        # Get the deck name from the user using the GUI dialog
        deck_name = get_deck_name()
        print(f"Using deck name: {deck_name}")
    except Exception as e:
        # If there's an error with the GUI dialog, fall back to console input
        print(f"Error with GUI dialog: {e}")
        print("Falling back to console input...")
        deck_name = get_deck_name_fallback()
    
    # Create the orchestrator with the provided deck name
    orchestrator = Orchestrator(deck_name=deck_name)
    
    print(f"AnkiLive is running.")
    print(f"Press {orchestrator.capture_shortcut} to capture a screenshot (can be used multiple times).")
    print(f"Press {orchestrator.create_card_shortcut} to open the flashcard dialog with all captured screenshots.")
    print(f"Press {orchestrator.reset_shortcut} to reset all captured screenshots.")
    print(f"Press {orchestrator.exit_shortcut} to export the deck and exit.")
    print(f"You can also click the 'Add Screenshot' button in the dialog to capture more screenshots.")
    
    # Keep the program running until the exit shortcut is pressed
    # The exit functionality is now handled by the orchestrator
    try:
        # Just keep the main thread alive
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        orchestrator.export_deck()
        print("Exiting AnkiLive.")


if __name__ == "__main__":
    main()
