"""
Deck name input dialog for AnkiLive.

This module provides a lightweight dialog for getting the deck name input
at application startup.
"""

import tkinter as tk
from tkinter import ttk
from src.ui.input_dialog import get_root, reset_root

class DeckNameDialog:
    """A lightweight dialog for getting the deck name input."""

    def __init__(self, parent=None, default_name="AnkiLive"):
        """
        Initialize the dialog.
        
        Args:
            parent: Optional parent window
            default_name: Default deck name to pre-fill
        """
        # Use the provided parent or get the global root
        self.parent = parent if parent is not None else get_root()
        
        # Create the dialog window
        self.root = tk.Toplevel(self.parent)
        self.root.title("AnkiLive - Deck Name")
        self.root.geometry("400x150")
        self.root.resizable(False, False)
        
        # Set up grid configuration
        self.root.columnconfigure(0, weight=1)
        
        # Create the main frame
        main_frame = ttk.Frame(self.root, padding="20 20 20 20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.columnconfigure(0, weight=1)
        
        # Create the instruction label
        ttk.Label(
            main_frame, 
            text="Please enter a name for your Anki deck:",
            wraplength=360
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        # Create the deck name entry
        self.deck_name_var = tk.StringVar(value=default_name)
        self.deck_name_entry = ttk.Entry(main_frame, width=40, textvariable=self.deck_name_var)
        self.deck_name_entry.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        # Create the button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, sticky="e")
        
        # Create the buttons
        ttk.Button(button_frame, text="Cancel", command=self.on_cancel).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="OK", command=self.on_ok).pack(side=tk.RIGHT)
        
        # Set focus to the deck name entry
        self.deck_name_entry.focus_set()
        self.deck_name_entry.select_range(0, tk.END)
        
        # Initialize result
        self.result = None
        
        # Center the dialog on the screen
        self.center_window()
        
        # Set up the protocol for window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_cancel)
        
        # Make this dialog modal
        self.root.transient(self.parent)
        self.root.grab_set()
        
        # Bind Enter to trigger the OK action
        self.root.bind("<Return>", lambda event: self.on_ok())
        
    def center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def on_ok(self):
        """Handle the OK button click."""
        deck_name = self.deck_name_var.get().strip()
        
        if not deck_name:
            # If empty, use the default name
            deck_name = "AnkiLive"
        
        self.result = deck_name
        
        # Destroy the window immediately
        if self.root.winfo_exists():
            self.root.destroy()
    
    def on_cancel(self):
        """Handle the cancel button click."""
        # Use default name if cancelled
        self.result = "AnkiLive"
        
        # Destroy the window immediately
        if self.root.winfo_exists():
            self.root.destroy()


def get_deck_name(parent=None, default_name="AnkiLive"):
    """
    Show a dialog to get the deck name from the user.
    
    Args:
        parent: Optional parent window
        default_name: Default deck name to pre-fill
    
    Returns:
        The deck name entered by the user, or the default name if cancelled
    """
    print("Opening deck name dialog...")
    
    try:
        # Create a new root window if needed
        if parent is None:
            parent = get_root()
            # Make sure the root window is visible
            parent.deiconify()
            print("Root window created and made visible")
        
        # Create the dialog
        dialog = DeckNameDialog(parent, default_name)
        print("Dialog created")
        
        # Force update to ensure dialog is shown
        parent.update()
        
        # Run a new mainloop for this dialog
        print("Waiting for dialog to close...")
        parent.wait_window(dialog.root)
        
        # Get the result
        result = dialog.result
        print(f"Dialog closed with result: {result}")
        
        # Clean up the root window if we created it
        if parent == get_root():
            # Check if there are no more toplevel windows
            if not parent.winfo_children() or all(not isinstance(child, tk.Toplevel) or not tk.Misc.winfo_exists(child)
                                               for child in parent.winfo_children()):
                parent.destroy()
                reset_root()
                print("Root window destroyed")
        
        return result
    except Exception as e:
        print(f"Error in get_deck_name: {e}")
        # Return default name in case of error
        return default_name


if __name__ == "__main__":
    # Test the dialog
    deck_name = get_deck_name()
    print(f"Deck name: {deck_name}")