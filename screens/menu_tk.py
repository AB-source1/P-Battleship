import tkinter as tk
from PIL import Image, ImageTk

class MenuTk:
    """
    A full-screen, scalable main menu in Tkinter styled like the original Pygame menu.
    Buttons: Play, Settings, Multiplayer, Pass and Play, Quit.
    """
    def __init__(self, on_play, on_settings, on_multiplayer, on_pass_and_play, on_quit):
        # Initialize window
        self.root = tk.Tk()
        self.root.title("Battleships")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="black")

        # Get screen size
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # Create canvas for background and title
        self.canvas = tk.Canvas(self.root,
                                width=self.screen_width,
                                height=self.screen_height,
                                highlightthickness=0)
        self.canvas.pack()

        # Load and scale background image
        bg_path = "resources/images/cartoon_loading.png"
        img = Image.open(bg_path)
        # Use LANCZOS resampling for high-quality scaling
        img = img.resize((self.screen_width, self.screen_height), Image.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_image)

        # Title text
        title_size = int(self.screen_height * 0.15)
        title_font = ("Helvetica", title_size, "bold")
        self.canvas.create_text(
            self.screen_width / 2,
            self.screen_height * 0.12,
            text="BATTLESHIPS",
            fill="#FDB933",
            font=title_font
        )

        # Button styling
        btn_size = int(self.screen_height * 0.06)
        btn_font = ("Helvetica", btn_size, "bold")
        btn_width = int(self.screen_width * 0.2)
        btn_height = int(self.screen_height * 0.08)

        # Callback bindings
        self.on_play = on_play
        self.on_settings = on_settings
        self.on_multiplayer = on_multiplayer
        self.on_pass_and_play = on_pass_and_play
        self.on_quit = on_quit

        # Define buttons: text, handler, color
        buttons = [
            ("Play", self._handle_play, "#1aae00"),
            ("Settings", self._handle_settings, "#555555"),
            ("Multiplayer", self._handle_multiplayer, "#0066cc"),
            ("Pass and Play", self._handle_pass_and_play, "#1aae00"),
            ("Quit", self._handle_quit, "#cc0000")
        ]

        # Vertical placement
        start_y = self.screen_height * 0.3
        spacing = btn_height + int(self.screen_height * 0.02)
        x_pos = self.screen_width * 0.15

        for i, (text, handler, color) in enumerate(buttons):
            btn = tk.Button(
                self.root,
                text=text,
                font=btn_font,
                fg="white",
                bg=color,
                activebackground=color,
                bd=3,
                relief="raised",
                highlightthickness=0,
                command=handler
            )
            # Embed button in canvas for absolute positioning
            self.canvas.create_window(
                x_pos,
                start_y + i * spacing,
                anchor="nw",
                window=btn,
                width=btn_width,
                height=btn_height
            )

    # Handlers destroy menu and call the provided callback
    def _handle_play(self):
        self.root.destroy()
        self.on_play()

    def _handle_settings(self):
        self.root.destroy()
        self.on_settings()

    def _handle_multiplayer(self):
        self.root.destroy()
        self.on_multiplayer()

    def _handle_pass_and_play(self):
        self.root.destroy()
        self.on_pass_and_play()

    def _handle_quit(self):
        self.root.destroy()
        self.on_quit()

    def run(self):
        self.root.mainloop()