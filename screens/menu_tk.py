# screens/menu_tk.py

import tkinter as tk
from PIL import Image, ImageTk
from core.config import Config
import tkinter.font as tkFont

class MenuTk:
    def __init__(self, state, on_play, on_settings, on_multiplayer, on_pass_and_play, on_quit):
        self.state = state

        # Build & center root
        self.root = tk.Tk()
        self.root.title("Battleships")
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        x = (sw - Config.WIDTH)//2
        y = (sh - Config.HEIGHT)//2
        self.root.geometry(f"{Config.WIDTH}x{Config.HEIGHT}+{x}+{y}")
        self.root.minsize(400,300)
        self.root.configure(bg="black")

        # Canvas + background
        self.canvas = tk.Canvas(self.root, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        bg = Image.open("resources/images/cartoon_loading.png")
        self.orig_bg = bg
        self.bg_img = ImageTk.PhotoImage(bg.resize((Config.WIDTH, Config.HEIGHT), Image.LANCZOS))
        self.bg_id  = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_img)
        self.canvas.image = self.bg_img  # hold reference

        # Callbacks
        self.on_play          = on_play
        self.on_settings      = on_settings
        self.on_multiplayer   = on_multiplayer
        self.on_pass_and_play = on_pass_and_play
        self.on_quit          = on_quit

        # Buttons
        self.buttons = []
        btn_info = [
            ("Play",          self._handle_play,         Config.GREEN),
            ("Settings",      self._handle_settings,     Config.GRAY),
            ("Multiplayer",   self._handle_multiplayer,  Config.BLUE),
            ("Pass & Play",   self._handle_pass_and_play,Config.GREEN),
            ("Quit",          self._handle_quit,         Config.RED)
        ]
        for text, handler, color in btn_info:
            b = tk.Button(
                self.root,
                text=text,
                fg="white",
                bg=self._hex(color),
                activebackground=self._hex(color),
                bd=2,
                relief="raised",
                highlightthickness=0,
                command=lambda cb=handler: self._on_button(cb)
            )
            self.buttons.append(b)

        # Place buttons
        relx, rely = 0.15, 0.30
        relw, relh = 0.20, 0.08
        spacing = relh + 0.02
        for i, btn in enumerate(self.buttons):
            btn.place(relx=relx, rely=rely + i*spacing, relwidth=relw, relheight=relh)

        # Resize handling
        self.resize_job = None
        self.root.bind("<Configure>", self._debounce_resize)
        self.root.bind("<Escape>", lambda e: self._on_button(self._handle_quit))

        # Initial font scaling
        self._rescale()

    def _hex(self, rgb):
        return "#{:02x}{:02x}{:02x}".format(*rgb)

    def _on_button(self, callback):
        # 1) Destroy **first** so callback never sees a dead window
        try:
            self.root.destroy()
        except tk.TclError:
            pass
        # 2) Then invoke the action
        callback()

    # — handler stubs just call your callbacks, no destroy here —
    def _handle_play(self):          self.on_play()
    def _handle_settings(self):      self.on_settings()
    def _handle_multiplayer(self):   self.on_multiplayer()
    def _handle_pass_and_play(self): self.on_pass_and_play()
    def _handle_quit(self):          self.on_quit()

    def _debounce_resize(self, event):
        if self.resize_job:
            self.root.after_cancel(self.resize_job)
        self.resize_job = self.root.after(100, self._rescale)

    def _rescale(self):
        # 1) resize bg
        w,h = self.root.winfo_width(), self.root.winfo_height()
        if w<100 or h<100: return
        bg = self.orig_bg.resize((w,h), Image.LANCZOS)
        self.bg_img = ImageTk.PhotoImage(bg)
        self.canvas.itemconfig(self.bg_id, image=self.bg_img)
        self.canvas.config(width=w, height=h)
        self.canvas.image = self.bg_img

        # 2) uniform font
        max_sz = max(8, int(h * 0.06))
        font = tkFont.Font(family="Helvetica", size=max_sz, weight="bold")
        longest = max(b.cget("text") for b in self.buttons)
        while font.measure(longest) > w*0.8 and font.cget("size") > 8:
            font.configure(size=font.cget("size") - 1)

        # 3) apply to all
        for btn in self.buttons:
            btn.config(font=(font.actual("family"), font.cget("size"), "bold"))

    def run(self):
        self.root.mainloop()
