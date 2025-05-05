"""
UI components for AnkiLive.

This package provides UI components for the AnkiLive application.
"""

from src.ui.input_dialog import get_flashcard_input, FlashcardInputDialog
from src.ui.deck_name_dialog import get_deck_name

__all__ = ["get_flashcard_input", "FlashcardInputDialog", "get_deck_name"]