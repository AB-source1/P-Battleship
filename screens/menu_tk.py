import tkinter as tk
from PIL import Image, ImageTk
from core.config import Config
import tkinter.font as tkFont

class MenuTk:
    def __init__(self, on_play, on_settings, on_multiplayer, on_pass_and_play, on_quit):
        self.root = tk.Tk()
        self.root.title("Battleships")
        self.root.geometry(f"{Config.WIDTH}x{Config.HEIGHT}")
        self.root.minsize(400, 300)
        self.root.configure(bg="black")

        self.canvas = tk.Canvas(self.root, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.original_bg = Image.open("resources/images/cartoon_loading.png")
        self.bg_image = ImageTk.PhotoImage(self.original_bg.resize((Config.WIDTH, Config.HEIGHT), Image.LANCZOS))
        self.canvas_bg = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_image)

        self.resize_after_id = None

        # user callbacks
        self.on_play            = on_play
        self.on_settings        = on_settings
        self.on_multiplayer     = on_multiplayer
        self.on_pass_and_play   = on_pass_and_play
        self.on_quit            = on_quit

        # button specs
        btn_info = [
            ("Play",           self._handle_play,         "#1aae00"),
            ("Settings",       self._handle_settings,     "#555555"),
            ("Pass and Play",  self._handle_pass_and_play,"#1aae00"),
            ("Quit",           self._handle_quit,         "#cc0000"),
        ]

        self.buttons = []
        relx = 0.15
        rely_start = 0.30
        btn_relwidth = 0.20
        btn_relheight = 0.08
        v_spacing = btn_relheight + 0.02

        for idx, (txt, handler, color) in enumerate(btn_info):
            btn = tk.Button(
                self.root,
                text=txt,
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

        # Initial sizing
        self._update_all_fonts()

        # bind resize + fullscreen toggle
        self.root.bind("<Configure>", self._debounced_resize)
        self.root.bind("<F11>", self._toggle_fullscreen)
        self.root.bind("<Escape>", self._exit_fullscreen)
        self.is_fullscreen = False

    def _on_button(self, callback):
        self.root.destroy()
        callback()

    def _toggle_fullscreen(self, e=None):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)

    def _exit_fullscreen(self, e=None):
        self.is_fullscreen = False
        self.root.attributes("-fullscreen", False)

    def _debounced_resize(self, event):
        if self.resize_after_id:
            self.root.after_cancel(self.resize_after_id)
        self.resize_after_id = self.root.after(150, self._on_resize)

    def _on_resize(self):
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        if w < 100 or h < 100:
            return

        # resize background
        resized = self.original_bg.resize((w, h), Image.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(resized)
        self.canvas.itemconfig(self.canvas_bg, image=self.bg_image)
        self.canvas.config(width=w, height=h)

        # adjust fonts on buttons
        self._update_all_fonts()

    def _update_all_fonts(self):
         # 1) Start at a base size (6% of height), down to a min of 8px
        height = self.root.winfo_height()
        max_size = int(height * 0.06)
        max_size = max(8, max_size)

        # 2) Find the largest size that fits *every* button
        for test_size in range(max_size, 7, -1):
            f = tkFont.Font(family="Helvetica", size=test_size, weight="bold")
            fits_all = True
            for btn in self.buttons:
                btn.update_idletasks()
                btn_w = btn.winfo_width()
                txt   = btn.cget("text")
                # if any label is too wide, this size doesn't work
                if f.measure(txt) > btn_w - 10:
                    fits_all = False
                    break
            if fits_all:
                # this test_size works for everyone
                final_font = f
                break
        else:
            # fallback to minimum
            final_font = tkFont.Font(family="Helvetica", size=8, weight="bold")

        # 3) Apply that same font to all buttons
        for btn in self.buttons:
            btn.config(font=final_font)

    # handlers for user actions
    def _handle_play(self):
        self.on_play(); self.root.destroy()
    def _handle_settings(self):
        self.on_settings(); self.root.destroy()
    def _handle_pass_and_play(self):
        self.on_pass_and_play(); self.root.destroy()
    def _handle_quit(self):
        self.on_quit(); self.root.destroy()

    def run(self):
        self.root.mainloop()
