# screens/menu_tk.py

import tkinter as tk
from PIL import Image, ImageTk
from core.config import Config
import tkinter.font as tkFont

def _hex(rgb_tuple):
    return "#{:02x}{:02x}{:02x}".format(*rgb_tuple)

class MenuTk:
    def __init__(self, state, on_play, on_settings, on_multiplayer, on_pass_and_play, on_quit):
        self.state = state
        self.on_play = on_play
        self.on_settings = on_settings
        self.on_multiplayer = on_multiplayer
        self.on_pass_and_play = on_pass_and_play
        self.on_quit = on_quit

        # ─── Build & center root ───────────────────────────────
        self.root = tk.Tk()
        self.root.title("Battleships")
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        x = (sw - Config.WIDTH)//2
        y = (sh - Config.HEIGHT)//2
        self.root.geometry(f"{Config.WIDTH}x{Config.HEIGHT}+{x}+{y}")
        self.root.minsize(400, 300)
        self.root.configure(bg="black")

        # ─── Canvas + background ───────────────────────────────
        self.canvas = tk.Canvas(self.root, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.orig_bg = Image.open("resources/images/cartoon_loading.png")
        self._resize_bg(Config.WIDTH, Config.HEIGHT)

        # ─── Build buttons ──────────────────────────────────────
        self.buttons = []
        btn_info = [
            ("Play",          self.on_play,         Config.GREEN),
            ("Settings",      self.on_settings,     Config.GRAY),
            ("Multiplayer",   self.on_multiplayer,  Config.BLUE),
            ("Pass & Play",   self.on_pass_and_play,Config.GREEN),
            ("Quit",          self.on_quit,         Config.RED),
        ]
        for text, handler, color in btn_info:
            b = tk.Button(
                self.root,
                text=text,
                fg="white",
                bg=_hex(color),
                activebackground=_hex(color),
                bd=2,
                relief="raised",
                highlightthickness=0,
                command=lambda cb=handler: self._on_button(cb)
            )
            self.buttons.append(b)

        # ─── Fixed geometry ─────────────────────────────────────
        self._relx, self._rely = 0.15, 0.30
        self._relw, self._relh = 0.20, 0.08
        self._spacing = self._relh + 0.02

        # ─── Bind resize ────────────────────────────────────────
        self.resize_job = None
        self.root.bind("<Configure>", self._debounce_resize)
        self.root.bind("<Escape>", lambda e: self._on_button(self.on_quit))

        # ─── Initial layout ────────────────────────────────────
        self._layout_buttons()

    def _on_button(self, callback):
        # Destroy first so no TclErrors, then run callback
        self.root.destroy()
        callback()

    def _debounce_resize(self, event):
        if self.resize_job:
            self.root.after_cancel(self.resize_job)
        self.resize_job = self.root.after(100, self._layout_buttons)

    def _resize_bg(self, w, h):
        bg = self.orig_bg.resize((w, h), Image.LANCZOS)
        self.bg_img = ImageTk.PhotoImage(bg)
        if hasattr(self, "_bg_id"):
            self.canvas.itemconfig(self._bg_id, image=self.bg_img)
        else:
            self._bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_img)
        self.canvas.image = self.bg_img

    def _layout_buttons(self):
        w, h = self.root.winfo_width(), self.root.winfo_height()
        if w < 100 or h < 100:
            return

        # 1) background
        self._resize_bg(w, h)

        # 2) compute each button's pixel width
        btn_px_width = int(self._relw * w)

        # 3) find the largest initial font size
        #    start at 60% of button height, down to min 6px
        max_font_sz = max(6, int(h * self._relh * 0.6))
        chosen = 6
        for sz in range(max_font_sz, 5, -1):
            f = tkFont.Font(family="Helvetica", size=sz, weight="bold")
            # check longest label
            if all(f.measure(b.cget("text")) <= btn_px_width * 0.8 for b in self.buttons):
                chosen = sz
                break

        # 4) extra per-button check: some labels may still overflow due to kerning
        f = tkFont.Font(family="Helvetica", size=chosen, weight="bold")
        overflow = True
        while overflow and chosen > 6:
            overflow = False
            for btn in self.buttons:
                if f.measure(btn.cget("text")) > btn_px_width * 0.8:
                    chosen -= 1
                    f.configure(size=chosen)
                    overflow = True
                    break

        uniform_font = ("Helvetica", chosen, "bold")

        # 5) place buttons
        for i, btn in enumerate(self.buttons):
            btn.config(font=uniform_font)
            btn.place(
                relx=self._relx,
                rely=self._rely + i * self._spacing,
                relwidth=self._relw,
                relheight=self._relh
            )

    def run(self):
        self.root.mainloop()
