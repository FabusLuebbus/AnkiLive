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
    """Model for Anki cards with multiple screenshots, question, and answer."""
    
    def __init__(self):
        """Initialize the Anki card model."""
        self.model = genanki.Model(
            ANKI_MODEL_ID,
            'AnkiLive Card',
            fields=[
                {'name': 'Question'},
                {'name': 'Answer'},
                {'name': 'Screenshots'},
            ],
            templates=[
                {
                    'name': 'Card 1',
                    'qfmt': '{{Question}}',
                    'afmt': '{{FrontSide}}<hr id="answer">{{Screenshots}}<br>{{Answer}}',
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
        self.cards_data_dir = os.path.join(cards_dir, "data")
        
        # Ensure directories exist
        os.makedirs(self.cards_dir, exist_ok=True)
        os.makedirs(self.media_dir, exist_ok=True)
        os.makedirs(self.cards_data_dir, exist_ok=True)

        self.load_saved_cards()
        
        # Initialize the model
        self.model = AnkiCardModel().model
        
        # Store notes in a list instead of immediately adding to deck
        self.notes = []
        
        # Track media files
        self.media_files = []
        
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
        
        # Add to media files list
        self.media_files.append(filepath)
        
        return filename
        
    def save_screenshots(self, screenshots: list[Image.Image]) -> list[str]:
        """
        Save multiple screenshots to the media directory.
        
        Args:
            screenshots: List of PIL Image objects containing the screenshots
            
        Returns:
            List of filenames of the saved screenshots
        """
        filenames = []
        for screenshot in screenshots:
            filename = self.save_screenshot(screenshot)
            filenames.append(filename)
        
        logger.info(f"Saved {len(filenames)} screenshots")
        return filenames
    
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
    
    def create_card(self, question: str, answer: str, screenshots: list[Image.Image]) -> str:
        """
        Create an Anki card with the given question, answer, and screenshots.
        Store it individually for later export.
        
        Args:
            question: The question text
            answer: The answer text
            screenshots: List of PIL Image objects containing the screenshots
            
        Returns:
            The ID of the created card
        """
        # Save the screenshots
        screenshot_filenames = self.save_screenshots(screenshots)
        
        # Create HTML for multiple screenshots
        screenshots_html = ""
        for filename in screenshot_filenames:
            screenshots_html += f'<img src="{filename}">'
        
        # Create a note
        note = genanki.Note(
            model=self.model,
            fields=[
                html.escape(question),
                self.convert_markdown_to_html(html.escape(answer)),
                screenshots_html
            ]
        )
        
        # Generate a unique ID for the card
        card_id = uuid.uuid4().hex
        
        # Store the note in our list
        self.notes.append(note)
        
        # Save card data to a file for persistence
        card_data = {
            'id': card_id,
            'question': question,
            'answer': answer,
            'screenshots': screenshot_filenames,
            'created_at': datetime.now().isoformat()
        }
        
        # Save to a JSON file
        import json
        card_file_path = os.path.join(self.cards_data_dir, f"{card_id}.json")
        with open(card_file_path, 'w') as f:
            json.dump(card_data, f, indent=2)
        
        logger.info(f"Created card: {question[:30]}... (ID: {card_id})")
        return card_id
    
    def build_deck(self) -> genanki.Deck:
        """
        Build the deck by adding all stored notes.
        
        Returns:
            The built deck
        """
        # Initialize a new deck
        deck = genanki.Deck(ANKI_DECK_ID, self.deck_name)
        
        # Add all notes to the deck
        for note in self.notes:
            deck.add_note(note)
        
        logger.info(f"Built deck with {len(self.notes)} cards")
        return deck
    
    def export_deck(self, filename: Optional[str] = None) -> str:
        """
        Export the deck to an .apkg file.
        
        This method exports the deck to an .apkg file and automatically
        cleans up all working data while preserving the exported deck.
        
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
        
        # Build the deck
        deck = self.build_deck()
        
        # Create a package and write it to a file
        package = genanki.Package(deck)
        package.media_files = self.media_files
        package.write_to_file(filepath)
        
        logger.info(f"Exported deck to {filepath} with {len(deck.notes)} cards and {len(self.media_files)} media files")
        
        self.teardown(keep_exported_deck=True)
        
        return filepath
    
    def teardown(self, keep_exported_deck: bool = True) -> None:
        """
        Clean up all working data after deck export.
        
        This method removes all temporary files created during the card creation process,
        including screenshots in the media directory and card data files.
        
        Args:
            keep_exported_deck: Whether to keep the exported .apkg file(s)
        """
        import shutil
        
        # Clear media files
        for media_file in self.media_files:
            try:
                if os.path.exists(media_file):
                    os.remove(media_file)
                    logger.info(f"Removed media file: {media_file}")
            except Exception as e:
                logger.error(f"Error removing media file {media_file}: {e}")
        
        # Clear card data files
        for card_file in os.listdir(self.cards_data_dir):
            if card_file.endswith('.json'):
                try:
                    os.remove(os.path.join(self.cards_data_dir, card_file))
                    logger.info(f"Removed card data file: {card_file}")
                except Exception as e:
                    logger.error(f"Error removing card data file {card_file}: {e}")
        
        # Optionally remove exported decks
        if not keep_exported_deck:
            for deck_file in os.listdir(self.cards_dir):
                if deck_file.endswith('.apkg'):
                    try:
                        os.remove(os.path.join(self.cards_dir, deck_file))
                        logger.info(f"Removed exported deck: {deck_file}")
                    except Exception as e:
                        logger.error(f"Error removing exported deck {deck_file}: {e}")
        
        # Reset internal state
        self.notes = []
        self.media_files = []
        
        logger.info("Teardown complete: all working data has been cleansed")
    
    def create_and_save_card(self, question: str, answer: str, screenshots: list[Image.Image]) -> str:
        """
        Create a card and store it.
        
        Args:
            question: The question text
            answer: The answer text
            screenshots: List of PIL Image objects containing the screenshots
            
        Returns:
            The ID of the created card
        """
        # Create the card
        return self.create_card(question, answer, screenshots)
    
    def load_saved_cards(self) -> None:
        """
        Load previously saved cards from the cards data directory.
        """
        import json
        
        # Clear existing notes
        self.notes = []
        
        # Get all card data files
        card_files = [f for f in os.listdir(self.cards_data_dir) if f.endswith('.json')]
        
        for card_file in card_files:
            try:
                with open(os.path.join(self.cards_data_dir, card_file), 'r') as f:
                    card_data = json.load(f)
                
                # Create a note from the card data
                screenshots_html = ""
                
                # Handle both old format (single screenshot) and new format (multiple screenshots)
                if 'screenshot' in card_data:
                    # Old format with single screenshot
                    screenshots_html = f'<img src="{card_data["screenshot"]}">'
                    screenshot_path = os.path.join(self.media_dir, card_data['screenshot'])
                    if os.path.exists(screenshot_path) and screenshot_path not in self.media_files:
                        self.media_files.append(screenshot_path)
                elif 'screenshots' in card_data:
                    # New format with multiple screenshots
                    for screenshot_filename in card_data['screenshots']:
                        screenshots_html += f'<img src="{screenshot_filename}">'
                        screenshot_path = os.path.join(self.media_dir, screenshot_filename)
                        if os.path.exists(screenshot_path) and screenshot_path not in self.media_files:
                            self.media_files.append(screenshot_path)
                
                note = genanki.Note(
                    model=self.model,
                    fields=[
                        html.escape(card_data['question']),
                        self.convert_markdown_to_html(html.escape(card_data['answer'])),
                        screenshots_html
                    ]
                )
                
                # Add the note to our list
                self.notes.append(note)
                
            except Exception as e:
                logger.error(f"Error loading card from {card_file}: {e}")
        
        logger.info(f"Loaded {len(self.notes)} cards from saved data")