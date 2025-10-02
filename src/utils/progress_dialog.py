"""
Progress dialog utility for displaying AI generation progress
"""

import tkinter as tk
from tkinter import ttk
import threading


class ProgressDialog:
    """Display a progress dialog for long-running operations"""

    def __init__(self, parent, title="処理中...", message="処理を実行しています..."):
        self.parent = parent
        self.title = title
        self.message = message
        self.dialog = None
        self.label = None
        self.progress_bar = None
        self.cancelled = False

    def show(self):
        """Show the progress dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(self.title)
        self.dialog.geometry("400x150")
        self.dialog.resizable(False, False)

        # Center the dialog
        self.dialog.transient(self.parent)
        # Don't use grab_set() - it can cause issues with background threads

        # Message label
        self.label = tk.Label(
            self.dialog,
            text=self.message,
            font=("Arial", 12),
            wraplength=350
        )
        self.label.pack(pady=20)

        # Progress bar (indeterminate mode)
        self.progress_bar = ttk.Progressbar(
            self.dialog,
            mode='indeterminate',
            length=350
        )
        self.progress_bar.pack(pady=10)
        self.progress_bar.start(10)

        # Center on screen
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

        # Prevent closing
        self.dialog.protocol("WM_DELETE_WINDOW", lambda: None)

    def update_message(self, message):
        """Update the message displayed in the dialog"""
        if self.label:
            self.label.config(text=message)
            # Don't call dialog.update() - updates should be scheduled on main thread

    def close(self):
        """Close the progress dialog"""
        if self.dialog:
            self.progress_bar.stop()
            # No need to call grab_release() since we don't use grab_set()
            self.dialog.destroy()
            self.dialog = None


class AIGenerationDialog:
    """Specific dialog for AI character generation"""

    def __init__(self, parent):
        self.parent = parent
        self.dialog = None
        self.label = None
        self.progress_bar = None
        self.detail_label = None

    def show(self, total_characters=1):
        """Show the AI generation dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("AI キャラクター生成中")
        self.dialog.geometry("450x180")
        self.dialog.resizable(False, False)

        # Center the dialog
        self.dialog.transient(self.parent)
        # Don't use grab_set() - it can cause issues with background threads

        # Title label
        title_label = tk.Label(
            self.dialog,
            text="🤖 AIがキャラクターを分析しています...",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=15)

        # Message label
        self.label = tk.Label(
            self.dialog,
            text=f"空のステータスを持つキャラクターが {total_characters} 体見つかりました",
            font=("Arial", 11)
        )
        self.label.pack(pady=5)

        # Detail label
        self.detail_label = tk.Label(
            self.dialog,
            text="画像をダウンロード中...",
            font=("Arial", 10),
            fg="gray"
        )
        self.detail_label.pack(pady=5)

        # Progress bar (indeterminate mode)
        self.progress_bar = ttk.Progressbar(
            self.dialog,
            mode='indeterminate',
            length=400
        )
        self.progress_bar.pack(pady=15)
        self.progress_bar.start(8)

        # Center on screen
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

        # Prevent closing
        self.dialog.protocol("WM_DELETE_WINDOW", lambda: None)

    def update_progress(self, current, total, character_name=None, step=""):
        """Update progress information"""
        if self.label:
            self.label.config(text=f"処理中: {current} / {total} 体")

        if self.detail_label and step:
            if character_name:
                self.detail_label.config(text=f"{step} ({character_name})")
            else:
                self.detail_label.config(text=step)

        # Don't call dialog.update() - updates are already scheduled on main thread

    def close(self):
        """Close the dialog"""
        if self.dialog:
            self.progress_bar.stop()
            # No need to call grab_release() since we don't use grab_set()
            self.dialog.destroy()
            self.dialog = None
