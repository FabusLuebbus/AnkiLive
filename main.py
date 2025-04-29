"""
AnkiLive - A tool for creating Anki flashcards from lecture slides.

This is the main entry point for the application.
"""

import logging
from pynput import keyboard
from src.orchestrator import Orchestrator


def main():
    """Run the AnkiLive application."""
    # Configure logging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create the orchestrator (registers keyboard shortcut)
    orchestrator = Orchestrator()
    
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
