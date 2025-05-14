# screens/menu_render.py

import tkinter as tk
from core.config import Config


class MenuRender:
    def __init__(self, logic):
        self.logic = logic
        self.window = None

    def draw(self, screen, state):
        if self.window is not None:
            return  # Prevent reopening

        self.window = tk.Tk()
        self.window.title("P-Battleship")
        self.window.geometry(f"{Config.WIDTH}x{Config.HEIGHT}")
        self.window.configure(bg="#0077B6")

        title = tk.Label(
            self.window,
            text="BATTLESHIPS",
            font=("Helvetica", 36, "bold"),
            fg="orange",
            bg="#0077B6"
        )
        title.pack(pady=60)

        button_style = {
            "width": 20,
            "height": 2,
            "font": ("Helvetica", 14, "bold"),
            "bg": "#FFCC00",
            "fg": "white",
            "activebackground": "#C89600",
            "relief": "raised",
            "bd": 3
        }

        def wrap_and_close(func):
            def wrapper():
                self.window.destroy()
                self.window = None
                func()
            return wrapper

        buttons = [
            ("Play", wrap_and_close(self.logic.start_game)),
            ("Settings", wrap_and_close(self.logic.open_settings)),
            ("Multiplayer", wrap_and_close(self.logic.go_to_lobby)),
            ("Quit", self.logic.quit)
        ]

        for text, command in buttons:
            tk.Button(self.window, text=text, command=command, **button_style).pack(pady=10)

        self.window.mainloop()

