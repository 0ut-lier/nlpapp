"""Tkinter interface for NLPApp."""
from __future__ import annotations

import threading
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

from myapi import API, APIError
from mydb import Database, DatabaseError


class NLPApp:
    def __init__(self, root: tk.Tk | None = None) -> None:
        self.dbo = Database()
        self.apio = API()
        self.root = root or tk.Tk()
        self.root.title("NLPApp")
        self.root.geometry("350x600")
        self.root.configure(bg="red")
        self.root.minsize(320, 500)

        icon_path = Path(__file__).parent / "resources" / "favicon.ico"
        if icon_path.is_file():
            try:
                self.root.iconbitmap(str(icon_path))
            except tk.TclError:
                # The app remains usable if the platform cannot load .ico files.
                pass

        self.login_gui()
        if root is None:
            self.root.mainloop()

    def _heading(self, text: str = "NLP Application GUI") -> None:
        heading = tk.Label(
            self.root, text=text, bg="red", fg="white",
            font=("verdana", 18, "italic"),
        )
        heading.pack(pady=(30, 30))

    def clear(self) -> None:
        for widget in self.root.pack_slaves():
            widget.destroy()

    def login_gui(self) -> None:
        self.clear()
        self._heading()
        tk.Label(self.root, text="Enter your email").pack(pady=(10, 10))
        self.email_input = tk.Entry(self.root, width=30)
        self.email_input.pack(pady=(5, 10), ipady=3)
        tk.Label(self.root, text="Enter your password").pack(pady=(10, 10))
        self.password_input = tk.Entry(self.root, width=30, show="*")
        self.password_input.pack(pady=(5, 10), ipady=3)
        tk.Button(
            self.root, text="LOGIN", width=20, height=2,
            command=self.perform_login,
        ).pack(pady=(10, 10))
        tk.Label(self.root, text="Not a Member?").pack(pady=(20, 10))
        tk.Button(
            self.root, text="Register Now", command=self.register_gui
        ).pack(pady=(10, 10))

    def register_gui(self) -> None:
        self.clear()
        self._heading()
        tk.Label(self.root, text="Enter your name").pack(pady=(10, 10))
        self.name_input = tk.Entry(self.root, width=30)
        self.name_input.pack(pady=(5, 10), ipady=3)
        tk.Label(self.root, text="Enter your email").pack(pady=(10, 10))
        self.email_input = tk.Entry(self.root, width=30)
        self.email_input.pack(pady=(5, 10), ipady=3)
        tk.Label(self.root, text="Enter your password (8+ characters)").pack(
            pady=(10, 10)
        )
        self.password_input = tk.Entry(self.root, width=30, show="*")
        self.password_input.pack(pady=(5, 10), ipady=3)
        tk.Button(
            self.root, text="REGISTER", width=20, height=2,
            command=self.perform_registration,
        ).pack(pady=(10, 10))
        tk.Label(self.root, text="Already a Member?").pack(pady=(20, 10))
        tk.Button(
            self.root, text="Login Now", command=self.login_gui
        ).pack(pady=(10, 10))

    def perform_registration(self) -> None:
        try:
            created = self.dbo.add_data(
                self.name_input.get(),
                self.email_input.get(),
                self.password_input.get(),
            )
        except ValueError as exc:
            messagebox.showerror("Invalid details", str(exc))
            return
        except DatabaseError as exc:
            messagebox.showerror("Database error", str(exc))
            return

        if created:
            messagebox.showinfo(
                "Success", "Registration successful. You can login now."
            )
            self.login_gui()
        else:
            messagebox.showerror("Error", "Email already exists.")

    def perform_login(self) -> None:
        try:
            authenticated = self.dbo.search(
                self.email_input.get(), self.password_input.get()
            )
        except DatabaseError as exc:
            messagebox.showerror("Database error", str(exc))
            return
        if authenticated:
            messagebox.showinfo("Success", "Login successful.")
            self.home_gui()
        else:
            messagebox.showerror("Error", "Incorrect email or password.")

    def home_gui(self) -> None:
        self.clear()
        self._heading()
        for label, callback in (
            ("Sentiment Analysis", self.sentiment_gui),
            ("Named Entity Recognition", self.ner_gui),
            ("Emotion Detection", self.emotion_gui),
        ):
            tk.Button(
                self.root, text=label, width=25, height=3, command=callback
            ).pack(pady=(10, 10))
        tk.Button(
            self.root, text="Logout", command=self.login_gui
        ).pack(pady=(10, 10))

    def sentiment_gui(self) -> None:
        self.nlp_task_gui("sentiment-analysis")

    def ner_gui(self) -> None:
        self.nlp_task_gui("ner")

    def emotion_gui(self) -> None:
        self.nlp_task_gui("emotion-detection")

    def nlp_task_gui(self, task: str) -> None:
        headings = {
            "sentiment-analysis": ("Sentiment Analysis", "Analyze Sentiment"),
            "ner": ("Named Entity Recognition", "Do Named Entity Recognition"),
            "emotion-detection": ("Emotion Detection", "Do Emotion Detection"),
        }
        if task not in headings:
            messagebox.showerror("Error", "Unsupported NLP task.")
            self.home_gui()
            return

        self.clear()
        self._heading()
        heading_text, button_text = headings[task]
        tk.Label(
            self.root, text=heading_text, bg="red", fg="white",
            font=("verdana", 14),
        ).pack(pady=(10, 20))
        tk.Label(self.root, text="Enter the text").pack(pady=(20, 10))
        self.nlp_task_input = tk.Entry(self.root, width=30)
        self.nlp_task_input.pack(pady=(5, 10), ipady=3)
        self.nlp_task_button = tk.Button(
            self.root, text=button_text,
            command=lambda: self.do_nlp_task(task),
        )
        self.nlp_task_button.pack(pady=(10, 10))
        self.nlp_task_result = tk.Label(
            self.root, text="", bg="red", fg="white",
            font=("verdana", 12, "bold"), wraplength=300,
        )
        self.nlp_task_result.pack(pady=(20, 10))
        tk.Button(
            self.root, text="Go Back", command=self.home_gui
        ).pack(pady=(10, 10))

    def do_nlp_task(self, task: str) -> None:
        text = self.nlp_task_input.get().strip()
        if not text:
            messagebox.showerror("Input required", "Please enter some text to analyze.")
            return

        self.nlp_task_button.config(state=tk.DISABLED)
        self.nlp_task_result.config(text="Analyzing...")

        def worker() -> None:
            try:
                result = self.apio.nlp_task(task, text)
                self.root.after(0, self._show_result, result, None)
            except (APIError, ValueError) as exc:
                self.root.after(0, self._show_result, None, str(exc))
            except Exception:
                # Avoid exposing internals or user text in an unexpected-error dialog.
                self.root.after(
                    0, self._show_result, None,
                    "An unexpected error occurred while analyzing the text.",
                )

        threading.Thread(target=worker, daemon=True).start()

    def _show_result(self, result: str | None, error: str | None) -> None:
        try:
            self.nlp_task_button.config(state=tk.NORMAL)
            self.nlp_task_result.config(text=error or result or "")
            if error:
                messagebox.showerror("NLP service error", error)
        except tk.TclError:
            # The user may have navigated away or closed the window mid-request.
            pass


if __name__ == "__main__":
    NLPApp()
