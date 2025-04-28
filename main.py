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
    
    print(f"AnkiLive is running. Press {orchestrator.shortcut} to capture a screenshot.")
    print("Press ESC to exit.")
    
    # Keep the program running until ESC is pressed
    # Create a function to check for ESC key
    def on_press(key):
        try:
            # Check if the key is ESC
            if key == keyboard.Key.esc:
                print("Exiting AnkiLive.")
                # Stop the listener
                return False
        except AttributeError:
            pass
        return True
    
    # Create and start a keyboard listener
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


if __name__ == "__main__":
    main()
