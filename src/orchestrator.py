"""
Orchestrator for AnkiLive.

This module provides the main orchestration logic for the application,
coordinating between different services and UI components, including
dependency injection and environment setup.
"""

import os
import sys
import logging
from typing import Optional

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image
from pynput import keyboard

from src.screenshot.gnome_screenshot_client import ScreenshotClient, GnomeScreenshotClient
from src.ui import get_flashcard_input
from src.anki_card_repository import AnkiCardRepository
from src.ui.input_dialog import FlashcardInputDialog

# Configure logging
logger = logging.getLogger(__name__)


class Orchestrator:
    """Main orchestrator for AnkiLive application."""
    
    def __init__(
        self,
        cards_dir: str = "cards",
        deck_name: str = "AnkiLive",
    ):
        """
        Initialize the orchestrator.
        
        Args:
            cards_dir: Directory to store card files
            deck_name: Name of the Anki deck
            container: Optional DI container to use
            settings_override: Optional settings to override
            screenshot_client: Optional screenshot client to use
        """
        # Store the cards directory and deck name
        self.cards_dir = cards_dir
        self.deck_name = deck_name
        
        # Ensure cards directory exists
        os.makedirs(cards_dir, exist_ok=True)
        
        self.screenshot_client: ScreenshotClient = GnomeScreenshotClient()
        
        # Initialize the Anki card repository with the deck name
        self.anki_repository = AnkiCardRepository(cards_dir=cards_dir, deck_name=deck_name)
        
        # Register keyboard shortcuts
        # Define shortcuts in pynput format: a sequence of keys
        self.capture_shortcut = "<ctrl>+<shift>+<alt>+s"  # For capturing screenshots
        self.create_card_shortcut = "<ctrl>+<shift>+<alt>+c"  # For creating a card with captured screenshots
        self.reset_shortcut = "<ctrl>+<shift>+<alt>+r"  # For resetting captured screenshots
        self.exit_shortcut = "<ctrl>+<esc>"  # For exiting the application
        
        # Temporary storage for captured screenshots
        self.captured_screenshots = []
        
        # Set up the hotkey listeners using pynput
        self.capture_hotkey = keyboard.HotKey(
            keyboard.HotKey.parse(self.capture_shortcut),
            self.capture_and_store_screenshot
        )
        
        self.create_card_hotkey = keyboard.HotKey(
            keyboard.HotKey.parse(self.create_card_shortcut),
            self.open_card_dialog
        )
        
        self.reset_hotkey = keyboard.HotKey(
            keyboard.HotKey.parse(self.reset_shortcut),
            self.reset_screenshots
        )
        
        # Create a function to handle canonical key events
        def for_canonical(f):
            return lambda k: f(self.listener.canonical(k))
        
        # Start the keyboard listener
        self.listener = keyboard.Listener(
            on_press=for_canonical(lambda k: self.on_key_press(k)),
            on_release=for_canonical(lambda k: self.on_key_release(k))
        )
        self.listener.start()
        
        # Initialize dialog reference
        self.current_dialog = None
        
    
    def on_key_press(self, key):
        """Handle key press events."""
        self.capture_hotkey.press(key)
        self.create_card_hotkey.press(key)
        self.reset_hotkey.press(key)
    
    def on_key_release(self, key):
        """Handle key release events."""
        self.capture_hotkey.release(key)
        self.create_card_hotkey.release(key)
        self.reset_hotkey.release(key)
    
  

    def capture_screenshot(self):
        """
        Capture a screenshot using the screenshot client.
        
        Returns:
            The captured screenshot as a PIL Image, or None if capture failed
        """
        logger.info("Capturing screenshot...")
        print("Please select an area of the screen to capture...")
        
        try:
            screenshot = self.screenshot_client.get_screenshot()
            logger.info(f"Screenshot captured: {screenshot.width}x{screenshot.height}")
            return screenshot
        except Exception as e:
            logger.error(f"Error capturing screenshot: {str(e)}")
            print(f"Error: {str(e)}")
            return None
    
    def capture_and_store_screenshot(self):
        """Capture a screenshot and store it for later use."""
        screenshot = self.capture_screenshot()
        if screenshot is None:
            return
        
        # Add the screenshot to our temporary storage
        self.captured_screenshots.append(screenshot)
        print(f"Screenshot captured. Total screenshots: {len(self.captured_screenshots)}")
    
    def reset_screenshots(self):
        """Reset the captured screenshots."""
        if self.captured_screenshots:
            count = len(self.captured_screenshots)
            self.captured_screenshots = []
            print(f"Reset {count} captured screenshots.")
        else:
            print("No screenshots to reset.")
    
    def open_card_dialog(self):
        """Open the card dialog with all captured screenshots."""
        # Check if we have any screenshots
        if not self.captured_screenshots:
            print("No screenshots captured yet. Use the capture shortcut first.")
            return
        
        # Get question and answer inputs from the user
        logger.info("Getting flashcard inputs...")
        logger.info(f"Using {len(self.captured_screenshots)} previously captured screenshots")
        
        # Get flashcard input using the dialog
        result = get_flashcard_input(
            screenshots=self.captured_screenshots.copy(),
            screenshot_callback=self.capture_screenshot
        )
        
        # Force a garbage collection to ensure the dialog is properly cleaned up
        import gc
        gc.collect()
        
        if result is None:
            logger.info("Flashcard creation cancelled by user")
            return
        
        question, answer, screenshots = result
        logger.info(f"Flashcard inputs received - Question: {question[:30]}...")
        logger.info(f"Number of screenshots: {len(screenshots)}")
        
        # Reset the captured screenshots after creating a card
        self.captured_screenshots = []
        
        # Save card to Anki using genanki
        try:
            card_id = self.anki_repository.create_and_save_card(question, answer, screenshots)
            logger.info(f"Anki card created with ID: {card_id}")
            print(f"Flashcard created with question: {question}")
            print(f"Answer/notes: {answer[:50]}..." if len(answer) > 50 else f"Answer/notes: {answer}")
            print(f"Number of screenshots: {len(screenshots)}")
            print(f"Card ID: {card_id}")
        except Exception as e:
            logger.error(f"Error saving Anki card: {str(e)}")
            print(f"Error saving Anki card: {str(e)}")
        


    def export_deck(self) -> str:
        """
        Export all cards to an Anki deck file.
        Only exports decks that have more than 0 cards.
        
        Returns:
            The path to the exported deck file or None if no cards to export
        """
        # Check if there are any cards to export
        if len(self.anki_repository.notes) == 0:
            logger.info("No cards to export")
            print("No cards to export. Please create at least one card first.")
            return None
            
        try:
            apkg_path = self.anki_repository.export_deck()
            logger.info(f"Exported Anki deck to {apkg_path}")
            print(f"Anki deck exported to: {apkg_path}")
            return apkg_path
        except Exception as e:
            logger.error(f"Error exporting Anki deck: {str(e)}")
            print(f"Error exporting Anki deck: {str(e)}")
            return None

    def __del__(self):
        """Clean up resources when the object is destroyed."""
        # Stop the keyboard listener if it's running
        if hasattr(self, 'listener') and self.listener.is_alive():
            self.listener.stop()
            self.listener.join()
