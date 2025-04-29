# AnkiLive

A tool for creating Anki flashcards from lecture slides.

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
- Dependencies:
  - tkinter (included with Python)
  - keyboard
  - Pillow (PIL)

## Installation

1. Clone this repository
2. Install Python dependencies:
   ```
   uv add keyboard Pillow
   ```

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
python main.py
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

1. Click "Export to Anki" in the main window
2. Import the generated file into Anki

## Project Structure

- `main.py` - Main application entry point
- `screenshot.py` - Screen capture functionality
- `ui.py` - User interface components for card creation and management

## Future Improvements

- Direct integration with Anki API
- Custom card templates
- OCR for text extraction from slides
- Tagging and categorization of cards