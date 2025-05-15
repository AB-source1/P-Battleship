# screens/settings_tk.py

import tkinter as tk
from PIL import Image, ImageTk
import tkinter.font as tkFont
import pygame
from core.config import Config
from screens.settings_logic import SettingsLogic

def _hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)

class SettingsTk:
    def __init__(self, state, on_back):
        pygame.mixer.init()
        self.state   = state
        self.logic   = SettingsLogic(None, state)
        self.on_back = on_back

        # ─── Root window ───────────────────────────────────────────
        self.root = tk.Tk()
        self.root.title("Battleships Settings")
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        x = (sw - Config.WIDTH)//2
        y = (sh - Config.HEIGHT)//2
        self.root.geometry(f"{Config.WIDTH}x{Config.HEIGHT}+{x}+{y}")
        self.root.minsize(400, 300)

        # ─── Canvas + BG ───────────────────────────────────────────
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.orig_bg = Image.open("resources/images/cartoon_loading.png")
        self._resize_bg(Config.WIDTH, Config.HEIGHT)

        # ─── ← Back Button ──────────────────────────────────────────
        self.btn_back = tk.Button(
            self.root,
            text="← Back",
            bg=_hex(Config.GRAY),
            fg="white",
            activebackground=_hex(Config.DARK_GRAY),
            font=("Helvetica", 12, "bold"),
            command=self._on_back
        )

        # ─── Grid‐size Buttons ──────────────────────────────────────
        self.grid_buttons = []
        for size in (5, 10, 15):
            b = tk.Button(
                self.root,
                text=f"{size}×{size}",
                command=lambda s=size: self._apply_grid(s)
            )
            self.grid_buttons.append(b)

        # ─── Difficulty Buttons ────────────────────────────────────
        self.diff_buttons = []
        for lvl in Config.DIFFICULTIES:
            b = tk.Button(
                self.root,
                text=lvl,
                command=lambda L=lvl: self._apply_diff(L)
            )
            self.diff_buttons.append(b)

        # ─── Volume var (0–100) ─────────────────────────────────────
        self.vol_var = tk.DoubleVar(value=pygame.mixer.music.get_volume() * 100)

        # ─── SFX Checkbox ───────────────────────────────────────────
        self.sfx_var = tk.BooleanVar(value=self.state.sfxenabled)
        self.cb_sfx = tk.Checkbutton(
            self.root,
            text="Sound Effects",
            variable=self.sfx_var,
            command=self._on_sfx_toggle,
            bg=_hex(Config.GRAY),
            fg="white",
            selectcolor=_hex(Config.GRAY),
            activebackground=_hex(Config.DARK_GRAY),
            activeforeground="white",
        )

        # ─── Layout params ─────────────────────────────────────────
        self.back_geom = (0.02, 0.02, 0.15, 0.07)
        self.grid_row  = 0.25
        self.diff_row  = 0.45
        self.audio_row = 0.65
        self.btn_w,self.btn_h = 0.25,0.10
        self.spacing   = self.btn_w + 0.03

        # ─── Debounced resize & ESC ─────────────────────────────────
        self.resize_job = None
        self.root.bind("<Configure>", self._debounce)
        self.root.bind("<Escape>", lambda e: self._on_back())

        # ─── Initial layout ────────────────────────────────────────
        self._layout()

    def _on_back(self):
        self.root.destroy()
        self.on_back()

    def _apply_grid(self, size: int):
        self.logic.apply_grid_size(size)
        self._layout()

    def _apply_diff(self, level: str):
        self.logic.apply_difficulty(level)
        self._layout()

    def _on_sfx_toggle(self):
        # Flip our state flag
        self.state.sfxenabled = self.sfx_var.get()
        # Pause/unpause all channels (does NOT affect music stream)
        

    def _on_handle_drag(self, event):
        w = self.root.winfo_width()
        left  = w * 0.15
        right = w * 0.85
        x = max(left, min(right, event.x))
        pct = (x - left) / (right - left)
        self.vol_var.set(pct * 100)
        pygame.mixer.music.set_volume(pct)
        self._draw_canvas_slider()

    def _on_track_click(self, event):
        self._on_handle_drag(event)

    def _on_volume_change(self):
        pct = self.vol_var.get() / 100.0
        pygame.mixer.music.set_volume(pct)
        self._draw_canvas_slider()

    def _debounce(self, event):
        if self.resize_job:
            self.root.after_cancel(self.resize_job)
        self.resize_job = self.root.after(100, self._layout)

    def _resize_bg(self, w:int, h:int):
        img = self.orig_bg.resize((w,h), Image.LANCZOS)
        self.bg_img = ImageTk.PhotoImage(img)
        if hasattr(self, "_bg_id"):
            self.canvas.itemconfig(self._bg_id, image=self.bg_img)
        else:
            self._bg_id = self.canvas.create_image(0,0, anchor="nw", image=self.bg_img)
        self.canvas.image = self.bg_img

    def _draw_canvas_slider(self):
        self.canvas.delete("vol_track")
        self.canvas.delete("vol_handle")

        w, h = self.root.winfo_width(), self.root.winfo_height()
        left, right = w*0.15, w*0.85
        y = h*(self.audio_row + 0.04)

        # track
        self.canvas.create_line(left, y, right, y, fill="white", width=4, tags="vol_track")
        # handle
        pct = self.vol_var.get()/100.0
        hx  = left + (right-left)*pct
        r   = 10
        self.canvas.create_oval(hx-r, y-r, hx+r, y+r,
                                fill=_hex(Config.GREEN), outline="", tags="vol_handle")

        self.canvas.tag_bind("vol_handle","<B1-Motion>", self._on_handle_drag)
        self.canvas.tag_bind("vol_track", "<Button-1>",   self._on_track_click)

    def _layout(self):
        w, h = self.root.winfo_width(), self.root.winfo_height()
        if w<100 or h<100: return

        # redraw bg
        self._resize_bg(w, h)

        # place back
        bx,by,bw,bh = self.back_geom
        self.btn_back.place(relx=bx, rely=by, relwidth=bw, relheight=bh)

        # choose font size
        btn_px = int(self.btn_w * w)
        labels = [b.cget("text") for b in self.grid_buttons+self.diff_buttons]
        labels += ["Sound Effects","Master Volume"]
        longest = max(labels, key=len)
        max_sz = max(8, int(h*self.btn_h*0.6))
        chosen = 8
        for sz in range(max_sz,7,-1):
            f = tkFont.Font(family="Helvetica", size=sz, weight="bold")
            if f.measure(longest) <= btn_px*0.85:
                chosen=sz
                break
        uniform = ("Helvetica", chosen, "bold")

        # grid buttons
        for i,b in enumerate(self.grid_buttons):
            col = 0.15 + i*self.spacing
            b.config(font=uniform,
                     bg=_hex(Config.GREEN if Config.GRID_SIZE==int(b.cget("text").split("×")[0]) else Config.GRAY),
                     fg="white")
            b.place(relx=col, rely=self.grid_row, relwidth=self.btn_w, relheight=self.btn_h)

        # diff buttons
        for i,b in enumerate(self.diff_buttons):
            col = 0.15 + i*self.spacing
            b.config(font=uniform,
                     bg=_hex(Config.GREEN if self.state.difficulty==b.cget("text") else Config.GRAY),
                     fg="white")
            b.place(relx=col, rely=self.diff_row, relwidth=self.btn_w, relheight=self.btn_h)

        # master volume label
        self.canvas.delete("vol_label")
        self.canvas.create_text(
            w*0.5, h*(self.audio_row-0.06),
            text="Master Volume",
            font=uniform, fill="white",
            tags="vol_label"
        )

        # volume slider
        self._draw_canvas_slider()

        # SFX checkbox
        self.cb_sfx.config(font=uniform)
        self.cb_sfx.place(relx=0.40, rely=self.audio_row+0.10,
                          relwidth=0.3, relheight=0.08)

    def run(self):
        self.root.mainloop()
