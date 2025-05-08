# AnkiLive

A tool for creating Anki flashcards from lecture slides without having to jump back and forth between the pdf viewer and anki.

## Overview

AnkiLive streamlines the workflow of creating Anki flashcards from lecture slides. It allows you to:

1. Capture a portion of your screen (e.g., from a PDF lecture slide)
2. Add multiple screenshots to a single card if needed
3. Add a question and optional notes
4. Save the card for later export to Anki

## Features

- Global hotkey (Ctrl+Shift+Alt+S) to capture screenshots
- Global hotkey (Ctrl+Shift+Alt+C) to create a card with all captured screenshots
- Global hotkey (Ctrl+Shift+Alt+R) to reset captured screenshots
- Global hotkey (Ctrl+Esc) to export the deck and exit
- Interactive screen selection interface
- Support for multiple screenshots per card
- Card creation with question and notes
- Export to Anki-compatible format

## Requirements

- Python 3.13+
- Dependencies (automatically managed by uv):
  - tkinter (included with Python)
  - pynput (for keyboard shortcuts)
  - Pillow (PIL) (for image processing)
  - genanki (for creating and exporting Anki decks)
  - markdown (for converting markdown to HTML)

## Installation

1. Clone this repository
2. The project uses uv for dependency management, so all dependencies are already specified in pyproject.toml

3. Install system dependencies:

   **Ubuntu/Debian:**
   ```
   sudo apt-get install python3-tk
   ```

   **Fedora:**
   ```
   sudo dnf install python3-tkinter
   ```

   **Arch Linux:**
   ```
   sudo pacman -S tk
   ```

   **macOS (with Homebrew):**
   ```
   brew install python-tk
   ```

   **Windows:**
   Tkinter is included with the standard Python installer for Windows.

## Usage

Run the application:

```
uv run main.py
```

### Creating a Card

1. Open your lecture slides in any PDF viewer
2. Press Ctrl+Shift+Alt+S to capture a screenshot
   - You can capture multiple screenshots by pressing this shortcut multiple times
   - Each screenshot is stored temporarily
3. Press Ctrl+Shift+Alt+C to open the flashcard dialog with all captured screenshots
4. In the dialog:
   - You can add more screenshots by clicking the "Add Screenshot" button
   - You can remove unwanted screenshots by selecting them and clicking "Remove Selected"
5. Enter a question and optional notes
6. Click "Save" to create the card
7. To reset all captured screenshots without creating a card, press Ctrl+Shift+Alt+R
8. To export the deck and exit the application, press Ctrl+Esc

### Exporting to Anki

1. Press Ctrl+Esc to export the deck and exit the application
2. The deck will be exported as a .apkg file in the `cards` directory
3. Import the generated .apkg file into Anki

## Project Structure

- `main.py` - Main application entry point
- `src/` - Source code directory
  - `anki_card_repository.py` - Handles creating, storing, and exporting Anki cards
  - `orchestrator.py` - Main orchestrator coordinating between services and UI components
  - `screenshot/` - Screenshot functionality
    - `screenshot_client.py` - Abstract interface for screenshot clients
    - `gnome_screenshot_client.py` - Implementation using gnome-screenshot
  - `ui/` - User interface components
    - `deck_name_dialog.py` - Dialog for getting deck name at startup
    - `input_dialog.py` - Dialog for creating flashcards with screenshots
- `cards/` - Directory for storing card data and exported decks

## Features in Detail

### Markdown Support

The answer/notes field supports Markdown formatting:
- Use `*` or `-` for bullet points
- Basic text formatting (bold, italic, etc.)
- The markdown is converted to HTML when exported to Anki

### Multiple Screenshots per Card

You can add multiple screenshots to a single card:
- Capture screenshots one by one using the global hotkey
- Add them all to a single card
- Rearrange or remove screenshots as needed

### Persistent Storage

Cards are stored persistently:
- Each card is saved as a JSON file in the `cards/data` directory
- Screenshots are saved in the `cards/media` directory
- Cards are loaded when the application starts

## Future Improvements

- Direct integration with Anki API
- Custom card templates
- OCR for text extraction from slides
- Tagging and categorization of cards
- Support for additional screenshot tools beyond gnome-screenshot
- Cross-platform screenshot support