"""
Anki Card Repository for AnkiLive.

This module provides functionality to create and store Anki cards using genanki,
including handling of screenshots as media files.
"""

import os
import uuid
import logging
import html
from datetime import datetime
from typing import Optional, Tuple
from pathlib import Path

import genanki
import markdown
from PIL import Image

# Configure logging
logger = logging.getLogger(__name__)

# Define a model ID for our flashcards
# Generated using: random.randrange(1 << 30, 1 << 31)
ANKI_MODEL_ID = 1234567890  # Replace with a generated ID

# Define a deck ID for our flashcards
# Generated using: random.randrange(1 << 30, 1 << 31)
ANKI_DECK_ID = 2059400110  # Replace with a generated ID


class AnkiCardModel:
    """Model for Anki cards with screenshot, question, and answer."""
    
    def __init__(self):
        """Initialize the Anki card model."""
        self.model = genanki.Model(
            ANKI_MODEL_ID,
            'AnkiLive Card',
            fields=[
                {'name': 'Question'},
                {'name': 'Answer'},
                {'name': 'Screenshot'},
            ],
            templates=[
                {
                    'name': 'Card 1',
                    'qfmt': '{{Question}}',
                    'afmt': '{{FrontSide}}<hr id="answer">{{Screenshot}}<br>{{Answer}}',
                },
            ],
            css="""
            .card {
                font-family: Arial, sans-serif;
                font-size: 16px;
                text-align: left;
                color: black;
                background-color: white;
                padding: 20px;
            }
            img {
                max-width: 90%;
                max-height: 400px;
                display: block;
                margin: 10px auto;
            }
            hr {
                border: 1px solid #ddd;
            }
            small {
                color: #666;
                font-size: 12px;
            }
            """
        )


class AnkiCardRepository:
    """Repository for creating and storing Anki cards."""
    
    def __init__(self, cards_dir: str = "cards", deck_name: str = "AnkiLive"):
        """
        Initialize the repository.
        
        Args:
            cards_dir: Directory to store card files and media
            deck_name: Name of the Anki deck
        """
        self.cards_dir = cards_dir
        self.deck_name = deck_name
        self.media_dir = os.path.join(cards_dir, "media")
        
        # Ensure directories exist
        os.makedirs(self.cards_dir, exist_ok=True)
        os.makedirs(self.media_dir, exist_ok=True)
        
        # Initialize the model
        self.model = AnkiCardModel().model
        
        # Initialize the deck
        self.deck = genanki.Deck(ANKI_DECK_ID, deck_name)
        
        logger.info(f"Initialized AnkiCardRepository with cards directory: {cards_dir}")
    
    def save_screenshot(self, screenshot: Image.Image) -> str:
        """
        Save a screenshot to the media directory.
        
        Args:
            screenshot: PIL Image object containing the screenshot
            
        Returns:
            The filename of the saved screenshot
        """
        # Generate a unique filename
        filename = f"screenshot_{uuid.uuid4().hex}.png"
        filepath = os.path.join(self.media_dir, filename)
        
        # Save the image
        screenshot.save(filepath)
        logger.info(f"Saved screenshot to {filepath}")
        
        return filename
    
    def convert_markdown_to_html(self, text: str) -> str:
        """
        Convert markdown to HTML using the markdown package.
        
        Args:
            text: Text with markdown formatting
            
        Returns:
            Text with HTML formatting
        """
        # Use the markdown package to convert markdown to HTML
        # The 'extras' parameter enables additional markdown features
        return markdown.markdown(text, extensions=['extra'])
    
    def create_card(self, question: str, answer: str, screenshot: Image.Image) -> None:
        """
        Create an Anki card with the given question, answer, and screenshot.
        
        Args:
            question: The question text
            answer: The answer text
            screenshot: PIL Image object containing the screenshot
        """
        # Save the screenshot
        screenshot_filename = self.save_screenshot(screenshot)
        
        # Create a note
        note = genanki.Note(
            model=self.model,
            fields=[
                html.escape(question),
                self.convert_markdown_to_html(html.escape(answer)),
                f'<img src="{screenshot_filename}">'
            ]
        )
        
        # Add the note to the deck
        self.deck.add_note(note)
        logger.info(f"Added note to deck: {question[:30]}...")
    
    def save_deck(self, filename: Optional[str] = None) -> str:
        """
        Save the deck to an .apkg file.
        
        Args:
            filename: Optional filename for the .apkg file
            
        Returns:
            The path to the saved .apkg file
        """
        if filename is None:
            # Generate a filename based on the deck name and current date
            date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.deck_name.replace(' ', '_')}_{date_str}.apkg"
        
        # Ensure the filename has the .apkg extension
        if not filename.endswith('.apkg'):
            filename += '.apkg'
        
        # Create the full path
        filepath = os.path.join(self.cards_dir, filename)
        
        # Get all media files
        media_files = [os.path.join(self.media_dir, f) for f in os.listdir(self.media_dir)]
        
        # Create a package and write it to a file
        package = genanki.Package(self.deck)
        package.media_files = media_files
        package.write_to_file(filepath)
        
        logger.info(f"Saved deck to {filepath} with {len(self.deck.notes)} cards and {len(media_files)} media files")
        
        return filepath
    
    def create_and_save_card(self, question: str, answer: str, screenshot: Image.Image) -> str:
        """
        Create a card and save the deck in one operation.
        
        Args:
            question: The question text
            answer: The answer text
            screenshot: PIL Image object containing the screenshot
            
        Returns:
            The path to the saved .apkg file
        """
        # Create the card
        self.create_card(question, answer, screenshot)
        
        # Save the deck
        return self.save_deck()