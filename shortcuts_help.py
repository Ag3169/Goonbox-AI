"""Keyboard shortcuts help dialog."""

import tkinter as tk
from tkinter import ttk


KEYBOARD_SHORTCUTS = {
    "Global": [
        ("Ctrl+S", "Save current file (IDE Mode only)"),
        ("Escape", "Cancel dialogs / Close panels"),
    ],
    "Chat Mode": [
        ("Enter", "Send message"),
        ("Shift+Enter", "New line in message"),
        ("Ctrl+L", "Clear chat (clears local display)"),
    ],
    "IDE Mode": [
        ("Ctrl+S", "Save current file"),
        ("Ctrl+R", "Run code"),
        ("Ctrl+Shift+F", "Format code"),
    ],
    "Chat Management": [
        ("Right-Click", "Open chat context menu"),
        ("Delete (context menu)", "Delete chat"),
        ("Rename (context menu)", "Rename chat"),
    ],
    "Rename Dialog": [
        ("Enter", "Confirm rename"),
        ("Escape", "Cancel rename"),
    ],
}


class KeyboardShortcutsWindow(tk.Toplevel):
    """Window displaying keyboard shortcuts."""
    
    def __init__(self, parent: tk.Tk, colors: dict):
        """Initialize keyboard shortcuts window."""
        super().__init__(parent)
        self.title("Keyboard Shortcuts")
        self.geometry("600x500")
        self.resizable(True, True)
        
        self.colors = colors
        self.configure(bg=colors["panel"])
        
        self.transient(parent)
        self._build_ui()
        self._center_window()
    
    def _center_window(self) -> None:
        """Center window on parent."""
        self.update_idletasks()
        parent = self.master
        
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        
        self.geometry(f"+{int(x)}+{int(y)}")
    
    def _build_ui(self) -> None:
        """Build the UI."""
        # Header
        header = tk.Frame(self, bg=self.colors["panel"])
        header.pack(fill="x", padx=16, pady=(16, 12))
        
        tk.Label(
            header,
            text="⌨️ Keyboard Shortcuts",
            bg=self.colors["panel"],
            fg=self.colors["text"],
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor="w")
        
        tk.Label(
            header,
            text="Quick reference for common keyboard shortcuts",
            bg=self.colors["panel"],
            fg=self.colors["muted"],
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(4, 0))
        
        # Shortcuts display
        content_frame = tk.Frame(self, bg=self.colors["panel"])
        content_frame.pack(fill="both", expand=True, padx=16, pady=12)
        
        # Canvas for scrolling
        canvas = tk.Canvas(
            content_frame,
            bg=self.colors["panel"],
            highlightthickness=0,
            bd=0,
        )
        canvas.pack(side="left", fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(
            content_frame,
            orient="vertical",
            command=canvas.yview,
            bg=self.colors["entry_bg"],
            troughcolor=self.colors["panel"],
            activebackground="#1c2740",
            bd=0,
            highlightthickness=0,
        )
        scrollbar.pack(side="right", fill="y")
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Inner frame for shortcuts
        inner_frame = tk.Frame(canvas, bg=self.colors["panel"])
        canvas_window = canvas.create_window((0, 0), window=inner_frame, anchor="nw")
        
        # Add shortcuts
        for category, shortcuts in KEYBOARD_SHORTCUTS.items():
            # Category label
            category_label = tk.Label(
                inner_frame,
                text=category,
                bg=self.colors["panel"],
                fg=self.colors["button"],
                font=("Segoe UI", 11, "bold"),
            )
            category_label.pack(anchor="w", pady=(12, 6))
            
            # Shortcuts in this category
            for shortcut, description in shortcuts:
                row = tk.Frame(inner_frame, bg=self.colors["panel"])
                row.pack(fill="x", pady=4)
                
                # Shortcut key (left)
                tk.Label(
                    row,
                    text=shortcut,
                    bg=self.colors["entry_bg"],
                    fg=self.colors["button"],
                    font=("Consolas", 9, "bold"),
                    padx=8,
                    pady=4,
                    width=15,
                    anchor="w",
                ).pack(side="left", padx=(0, 12))
                
                # Description (right)
                tk.Label(
                    row,
                    text=description,
                    bg=self.colors["panel"],
                    fg=self.colors["text"],
                    font=("Segoe UI", 9),
                    wraplength=300,
                    justify="left",
                ).pack(side="left", fill="x", expand=True)
        
        # Update scroll region
        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        inner_frame.bind("<Configure>", on_configure)
        
        # Mousewheel support
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Close button
        button_frame = tk.Frame(self, bg=self.colors["panel"])
        button_frame.pack(fill="x", padx=16, pady=(0, 16))
        
        tk.Button(
            button_frame,
            text="Close",
            command=self.destroy,
            bg=self.colors["button"],
            fg="#04100f",
            activebackground=self.colors["button_hover"],
            activeforeground="#04100f",
            bd=0,
            padx=20,
            pady=6,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
        ).pack(side="right")
