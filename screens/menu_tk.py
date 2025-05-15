import tkinter as tk
from PIL import Image, ImageTk
from core.config import Config

class MenuTk:
    """
    A resizable main menu in Tkinter styled like the original Pygame menu.
    Buttons: Play, Settings, Multiplayer, Pass and Play, Quit.
    """
    def __init__(self, on_play, on_settings, on_multiplayer, on_pass_and_play, on_quit):
        # Initialize window at Pygame config size, allow user to resize/collapse
        self.root = tk.Tk()
        self.root.title("Battleships")
        self.root.geometry(f"{Config.WIDTH}x{Config.HEIGHT}")
        self.root.minsize(400, 300)
        self.root.resizable(True, True)
        self.root.configure(bg="black")

        # Canvas for background
        self.canvas = tk.Canvas(self.root, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Load and draw background image at initial size
        bg = Image.open("resources/images/cartoon_loading.png")
        bg = bg.resize((Config.WIDTH, Config.HEIGHT), Image.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(bg)
        self.canvas_bg = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_image)

        # Store callbacks
        self.on_play = on_play
        self.on_settings = on_settings
        self.on_multiplayer = on_multiplayer
        self.on_pass_and_play = on_pass_and_play
        self.on_quit = on_quit

        # Define button details
        btn_info = [
            ("Play", self._handle_play, "#1aae00"),
            ("Settings", self._handle_settings, "#555555"),
            ("Multiplayer", self._handle_multiplayer, "#0066cc"),
            ("Pass and Play", self._handle_pass_and_play, "#1aae00"),
            ("Quit", self._handle_quit, "#cc0000")
        ]

        # Create & place buttons using relative geometry so they auto-scale
        self.buttons = []
        relx = 0.15
        rely_start = 0.30
        btn_relwidth = 0.20
        btn_relheight = 0.08
        v_spacing = btn_relheight + 0.02  # vertical spacing

        for idx, (text, handler, color) in enumerate(btn_info):
            btn = tk.Button(
                self.root,
                text=text,
                fg="white",
                bg=color,
                activebackground=color,
                bd=2,
                relief="raised",
                highlightthickness=0,
                command=lambda cb=handler: self._on_button(cb)
            )
            btn.place(
                relx=relx,
                rely=rely_start + idx * v_spacing,
                relwidth=btn_relwidth,
                relheight=btn_relheight
            )
            self.buttons.append(btn)

        # Initial font sizing
        self._update_button_fonts(Config.HEIGHT)
        # Bind resize event to update button fonts (size) dynamically
        self.root.bind("<Configure>", self._on_resize)

    def _on_button(self, callback):
        self.root.destroy()
        callback()

    def _on_resize(self, event):
        # Ignore events not related to height change
        try:
            new_height = event.height
        except AttributeError:
            return
        self._update_button_fonts(new_height)

    def _update_button_fonts(self, height):
        # Scale font size to ~6% of window height
        font_size = max(8, int(height * 0.06))
        for btn in self.buttons:
            btn.config(font=("Helvetica", font_size, "bold"))




    # Handlers destroy menu and call the provided callback
    def _handle_play(self):
        
        self.on_play()
        self.root.destroy()

    def _handle_settings(self):
        self.on_settings()
        self.root.destroy()

    def _handle_multiplayer(self):
        self.on_multiplayer()
        self.root.destroy()


    def _handle_pass_and_play(self):
        self.on_pass_and_play()
        self.root.destroy()


    def _handle_quit(self):
        self.on_quit()
        self.root.destroy()


    def run(self):
        self.root.mainloop()