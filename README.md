# AnkiLive

A tool for creating Anki flashcards from lecture slides.

## Overview

AnkiLive streamlines the workflow of creating Anki flashcards from lecture slides. It allows you to:

1. Capture a portion of your screen (e.g., from a PDF lecture slide)
2. Add a question and optional notes
3. Save the card for later export to Anki

## Features

- Global hotkey (Alt+S) to trigger screenshot capture
- Interactive screen selection interface
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
2. Press Alt+S or click "Capture Screenshot" in the AnkiLive window
3. Select the portion of the screen you want to capture
4. Enter a question and optional notes
5. Click "Save" to create the card

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