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

# Configure logging
logger = logging.getLogger(__name__)


class Orchestrator:
    """Main orchestrator for AnkiLive application."""
    
    def __init__(
        self,
        cards_dir: str = "cards",
    ):
        """
        Initialize the orchestrator.
        
        Args:
            cards_dir: Directory to store card files
            container: Optional DI container to use
            settings_override: Optional settings to override
            screenshot_client: Optional screenshot client to use
        """
        # Store the cards directory
        self.cards_dir = cards_dir
        
        # Ensure cards directory exists
        os.makedirs(cards_dir, exist_ok=True)
        
        self.screenshot_client: ScreenshotClient = GnomeScreenshotClient()
        
        # Initialize the Anki card repository
        self.anki_repository = AnkiCardRepository(cards_dir=cards_dir)
        
        # Register keyboard shortcut to trigger workflow
        # Define shortcut in pynput format: a sequence of keys
        self.shortcut = "<ctrl>+<shift>+<alt>+s"  # Human-readable version for display
        
        # Set up the hotkey listener using pynput
        self.hotkey = keyboard.HotKey(
            keyboard.HotKey.parse(self.shortcut),
            self.run
        )
        
        # Create a function to handle canonical key events
        def for_canonical(f):
            return lambda k: f(self.listener.canonical(k))
        
        # Start the keyboard listener
        self.listener = keyboard.Listener(
            on_press=for_canonical(self.hotkey.press),
            on_release=for_canonical(self.hotkey.release)
        )
        self.listener.start()
        
        logger.info(f"Registered keyboard shortcut: {self.shortcut}")

    def run(self):
        """Run the main application workflow."""
        # Get screenshot using the screenshot client
        logger.info("Capturing screenshot...")
        print("Please select an area of the screen to capture...")
        
        try:
            screenshot = self.screenshot_client.get_screenshot()
            logger.info(f"Screenshot captured: {screenshot.width}x{screenshot.height}")
        except Exception as e:
            logger.error(f"Error capturing screenshot: {str(e)}")
            print(f"Error: {str(e)}")
            return
        # Get question and answer inputs from the user
        logger.info("Getting flashcard inputs...")
        result = get_flashcard_input()
        
        if result is None:
            logger.info("Flashcard creation cancelled by user")
            return
        
        question, answer = result
        logger.info(f"Flashcard inputs received - Question: {question[:30]}...")
        
        # Save card to Anki using genanki
        try:
            card_id = self.anki_repository.create_and_save_card(question, answer, screenshot)
            logger.info(f"Anki card created with ID: {card_id}")
            print(f"Flashcard created with question: {question}")
            print(f"Answer/notes: {answer[:50]}..." if len(answer) > 50 else f"Answer/notes: {answer}")
            print(f"Card ID: {card_id}")
        except Exception as e:
            logger.error(f"Error saving Anki card: {str(e)}")
            print(f"Error saving Anki card: {str(e)}")
        


    def export_deck(self) -> str:
        """
        Export all cards to an Anki deck file.
        
        Returns:
            The path to the exported deck file
        """
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
