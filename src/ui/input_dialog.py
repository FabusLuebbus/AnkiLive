"""
Input dialog for AnkiLive.

This module provides a lightweight dialog for getting question and answer inputs
for flash cards.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Tuple

# Global root window to prevent multiple root windows
_root = None

def get_root():
    """Get or create the root window."""
    global _root
    if _root is None or not tk.Misc.winfo_exists(_root):
        _root = tk.Tk()
        _root.withdraw()  # Hide the root window
    return _root

def reset_root():
    """Reset the global root window reference."""
    global _root
    _root = None


class FlashcardInputDialog:
    """A lightweight dialog for getting question and answer inputs for flash cards."""

    def __init__(self, parent=None):
        """
        Initialize the dialog.
        
        Args:
            parent: Optional parent window
        """
        # Use the provided parent or get the global root
        self.parent = parent if parent is not None else get_root()
        
        # Create the dialog window
        self.root = tk.Toplevel(self.parent)
        self.root.title("Create Flashcard")
        self.root.geometry("500x400")
        self.root.resizable(True, True)
        self.root.protocol("WM_DELETE_WINDOW", self.on_cancel)
        
        # Make the dialog modal
        self.root.transient(parent)
        self.root.grab_set()
        
        # Set up grid configuration
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)
        
        # Create the question label and entry
        question_frame = ttk.Frame(self.root)
        question_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        question_frame.columnconfigure(0, weight=1)
        
        ttk.Label(question_frame, text="Question:").grid(row=0, column=0, sticky="w")
        self.question_entry = ttk.Entry(question_frame, width=50)
        self.question_entry.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        
        # Create the answer label and text area
        answer_frame = ttk.Frame(self.root)
        answer_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        answer_frame.columnconfigure(0, weight=1)
        answer_frame.rowconfigure(1, weight=1)
        
        ttk.Label(answer_frame, text="Answer/Notes: (Markdown supported - use * or - for bullet points)").grid(row=0, column=0, sticky="w")
        
        # Create a text widget with scrollbar for multiline input
        self.answer_text = tk.Text(answer_frame, wrap=tk.WORD, height=10)
        self.answer_text.grid(row=1, column=0, sticky="nsew")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(answer_frame, orient="vertical", command=self.answer_text.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.answer_text["yscrollcommand"] = scrollbar.set
        
        # Create the button frame
        button_frame = ttk.Frame(self.root)
        button_frame.grid(row=2, column=0, sticky="se", padx=10, pady=10)
        
        # Create the buttons
        ttk.Button(button_frame, text="Cancel", command=self.on_cancel).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Save", command=self.on_save).pack(side=tk.RIGHT)
        
        # Set focus to the question entry
        self.question_entry.focus_set()
        
        # Initialize result
        self.result: Optional[Tuple[str, str]] = None
        
        # Center the dialog on the screen
        self.center_window()
    
    def center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def on_save(self):
        """Handle the save button click."""
        question = self.question_entry.get().strip()
        # Get text from the Text widget, preserving all internal linebreaks
        # Tkinter adds an extra newline at the end, so we need to handle that
        answer = self.answer_text.get("1.0", tk.END)
        # Remove only the last character if it's a newline (added by Tkinter)
        if answer and answer[-1] == '\n':
            answer = answer[:-1]
        
        if not question:
            # Show error if question is empty
            tk.messagebox.showerror("Error", "Question cannot be empty")
            return
        
        self.result = (question, answer)
        self.root.destroy()
    
    def on_cancel(self):
        """Handle the cancel button click."""
        self.result = None
        self.root.destroy()
    
    def show(self) -> Optional[Tuple[str, str]]:
        """
        Show the dialog and wait for user input.
        
        Returns:
            A tuple of (question, answer) if the user saves, or None if cancelled
        """
        # Wait for the window to be destroyed
        self.root.wait_window()
        return self.result


def get_flashcard_input(parent=None) -> Optional[Tuple[str, str]]:
    """
    Show a dialog to get flashcard input from the user.
    
    Args:
        parent: Optional parent window
    
    Returns:
        A tuple of (question, answer) if the user saves, or None if cancelled
    """
    try:
        dialog = FlashcardInputDialog(parent)
        result = dialog.show()
        
        # If we created our own root window and there are no other toplevel windows,
        # destroy the root to clean up resources
        if parent is None:
            root = get_root()
            if not root.winfo_children() or all(not isinstance(child, tk.Toplevel) or not tk.Misc.winfo_exists(child)
                                               for child in root.winfo_children()):
                root.destroy()
                reset_root()  # Reset the global root reference
        
        return result
    except Exception as e:
        # If there's an error, make sure to reset the root reference
        if parent is None:
            reset_root()
        # Re-raise the exception
        raise


if __name__ == "__main__":
    # Test the dialog
    result = get_flashcard_input()
    if result:
        question, answer = result
        print(f"Question: {question}")
        print(f"Answer: {answer}")
    else:
        print("Cancelled")