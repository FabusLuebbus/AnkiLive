"""
Input dialog for AnkiLive.

This module provides a lightweight dialog for getting question, answer, and screenshots inputs
for flash cards.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Tuple, List
from PIL import Image, ImageTk

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
    """A lightweight dialog for getting question, answer, and screenshots inputs for flash cards."""

    def __init__(self, parent=None, screenshots=None, screenshot_callback=None):
        """
        Initialize the dialog.
        
        Args:
            parent: Optional parent window
            screenshots: Optional list of screenshots to initialize with
            screenshot_callback: Optional callback function to capture a new screenshot
        """
        # Store the screenshot callback
        self.screenshot_callback = screenshot_callback
        
        # Use the provided parent or get the global root
        self.parent = parent if parent is not None else get_root()
        
        # Initialize screenshots list
        self.screenshots = screenshots or []
        self.thumbnail_size = (100, 100)  # Size for screenshot thumbnails
        self.thumbnail_images = []  # Keep references to prevent garbage collection
        
        # Create the dialog window
        self.root = tk.Toplevel(self.parent)
        self.root.title("Create Flashcard")
        self.root.geometry("600x600")
        self.root.resizable(True, True)
        
        # Set up grid configuration
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(3, weight=1)
        
        # Create the question label and entry
        question_frame = ttk.Frame(self.root)
        question_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        question_frame.columnconfigure(0, weight=1)
        
        ttk.Label(question_frame, text="Question:").grid(row=0, column=0, sticky="w")
        self.question_entry = ttk.Entry(question_frame, width=50)
        self.question_entry.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        
        # Create the screenshots frame
        screenshots_frame = ttk.LabelFrame(self.root, text="Screenshots")
        screenshots_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        screenshots_frame.columnconfigure(0, weight=1)
        screenshots_frame.rowconfigure(1, weight=1)
        
        # Create a frame for the screenshot controls
        screenshot_controls = ttk.Frame(screenshots_frame)
        screenshot_controls.grid(row=0, column=0, sticky="ew", pady=5)
        
        # Add screenshot button
        self.add_screenshot_btn = ttk.Button(
            screenshot_controls,
            text="Add Screenshot",
            command=self.on_add_screenshot
        )
        self.add_screenshot_btn.pack(side=tk.LEFT, padx=5)
        
        # Remove screenshot button
        self.remove_screenshot_btn = ttk.Button(
            screenshot_controls,
            text="Remove Selected",
            command=self.on_remove_screenshot
        )
        self.remove_screenshot_btn.pack(side=tk.LEFT, padx=5)
        
        # Create a frame for the screenshot list
        self.screenshots_list_frame = ttk.Frame(screenshots_frame)
        self.screenshots_list_frame.grid(row=1, column=0, sticky="nsew", pady=5)
        self.screenshots_list_frame.columnconfigure(0, weight=1)
        self.screenshots_list_frame.rowconfigure(0, weight=1)
        
        # Create a canvas for the screenshots
        self.screenshots_canvas = tk.Canvas(self.screenshots_list_frame, bg="white")
        self.screenshots_canvas.grid(row=0, column=0, sticky="nsew")
        
        # Add scrollbar for the canvas
        scrollbar = ttk.Scrollbar(
            self.screenshots_list_frame,
            orient="horizontal",
            command=self.screenshots_canvas.xview
        )
        scrollbar.grid(row=1, column=0, sticky="ew")
        self.screenshots_canvas.configure(xscrollcommand=scrollbar.set)
        
        # Create a frame inside the canvas to hold the screenshots
        self.screenshots_container = ttk.Frame(self.screenshots_canvas)
        self.screenshots_canvas.create_window((0, 0), window=self.screenshots_container, anchor="nw")
        
        # Update the screenshots display
        self.update_screenshots_display()
        
        # Create the answer label and text area
        answer_frame = ttk.Frame(self.root)
        answer_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
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
        button_frame.grid(row=3, column=0, sticky="se", padx=10, pady=10)
        
        # Create the buttons
        ttk.Button(button_frame, text="Cancel", command=self.on_cancel).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Save", command=self.on_save).pack(side=tk.RIGHT)
        
        # Set focus to the question entry
        self.question_entry.focus_set()
        
        # Initialize result
        self.result = None
        
        # Center the dialog on the screen
        self.center_window()
        
        # Bind the configure event to update the canvas scrollregion
        self.screenshots_container.bind("<Configure>", self.on_frame_configure)
        
        # Set up the protocol for window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_cancel)
        
        # Bind Ctrl+Enter to trigger the save action
        self.root.bind("<Control-Return>", lambda event: self.on_save())
        
    def on_frame_configure(self, event):
        """Update the canvas scrollregion when the frame changes size."""
        self.screenshots_canvas.configure(scrollregion=self.screenshots_canvas.bbox("all"))
        
    def update_screenshots_display(self):
        """Update the screenshots display with the current screenshots."""
        # Clear the current display
        for widget in self.screenshots_container.winfo_children():
            widget.destroy()
        
        # Clear thumbnail references
        self.thumbnail_images = []
        
        # Add each screenshot to the display
        for i, screenshot in enumerate(self.screenshots):
            # Create a frame for this screenshot
            frame = ttk.Frame(self.screenshots_container)
            frame.pack(side=tk.LEFT, padx=5, pady=5)
            
            # Create a thumbnail of the screenshot
            thumbnail = screenshot.copy()
            thumbnail.thumbnail(self.thumbnail_size)
            
            # Convert to PhotoImage and keep a reference
            photo = ImageTk.PhotoImage(thumbnail)
            self.thumbnail_images.append(photo)
            
            # Create a label with the thumbnail
            label = ttk.Label(frame, image=photo)
            label.pack()
            
            # Add a selection indicator
            var = tk.BooleanVar(value=False)
            check = ttk.Checkbutton(frame, text=f"#{i+1}", variable=var)
            check.pack()
            
            # Store the variable in the frame for later access
            frame.var = var
    
    def center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def on_add_screenshot(self):
        """Handle the add screenshot button click."""
        if self.screenshot_callback:
            # Minimize the dialog temporarily to allow screenshot capture
            self.root.withdraw()
            
            # Capture the screenshot using the provided callback
            screenshot = self.screenshot_callback()
            
            # Restore the dialog
            self.root.deiconify()
            
            # Add the screenshot if it was captured successfully
            if screenshot:
                self.screenshots.append(screenshot)
                self.update_screenshots_display()
                print("Screenshot added to the current flashcard.")
        else:
            # Fallback if no callback is provided
            tk.messagebox.showinfo(
                "Add Screenshot",
                "Screenshot capture is not available."
            )
        
    def on_remove_screenshot(self):
        """Handle the remove screenshot button click."""
        # Get all frames in the screenshots container
        frames = self.screenshots_container.winfo_children()
        
        # Check which screenshots are selected for removal
        to_remove = []
        for i, frame in enumerate(frames):
            if hasattr(frame, 'var') and frame.var.get():
                to_remove.append(i)
        
        # Remove the selected screenshots in reverse order
        for i in sorted(to_remove, reverse=True):
            if 0 <= i < len(self.screenshots):
                del self.screenshots[i]
        
        # Update the display
        self.update_screenshots_display()
        
    def add_screenshot(self, screenshot):
        """
        Add a screenshot to the dialog.
        
        Args:
            screenshot: PIL Image object containing the screenshot
        """
        self.screenshots.append(screenshot)
        self.update_screenshots_display()
    
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
        
        if not self.screenshots:
            # Show error if no screenshots
            tk.messagebox.showerror("Error", "At least one screenshot is required")
            return
        
        self.result = (question, answer, self.screenshots)
        
        # Destroy the window immediately
        if self.root.winfo_exists():
            self.root.destroy()
    
    def on_cancel(self):
        """Handle the cancel button click."""
        self.result = None
        
        # Destroy the window immediately
        if self.root.winfo_exists():
            self.root.destroy()


def get_flashcard_input(parent=None, screenshots=None, screenshot_callback=None):
    """
    Show a dialog to get flashcard input from the user.
    
    Args:
        parent: Optional parent window
        screenshots: Optional list of screenshots to initialize with
        screenshot_callback: Optional callback function to capture a new screenshot
    
    Returns:
        A tuple of (question, answer, screenshots) if the user saves, or None if cancelled
    """
    # Create a new root window if needed
    if parent is None:
        parent = get_root()
    
    # Create the dialog
    dialog = FlashcardInputDialog(parent, screenshots, screenshot_callback)
    
    # Run a new mainloop for this dialog
    parent.wait_window(dialog.root)
    
    # Get the result
    result = dialog.result
    
    # Clean up the root window if we created it
    if parent == get_root():
        # Check if there are no more toplevel windows
        if not parent.winfo_children() or all(not isinstance(child, tk.Toplevel) or not tk.Misc.winfo_exists(child)
                                           for child in parent.winfo_children()):
            parent.destroy()
            reset_root()
    
    # Force garbage collection
    import gc
    gc.collect()
    
    return result


if __name__ == "__main__":
    # Test the dialog
    result = get_flashcard_input()
    if result:
        question, answer, screenshots = result
        print(f"Question: {question}")
        print(f"Answer: {answer}")
        print(f"Number of screenshots: {len(screenshots)}")
    else:
        print("Cancelled")