import tkinter as tk
from PIL import Image, ImageTk
import tkinter.font as tkFont
import pygame
from core.config import Config
from screens.settings_logic import SettingsLogic

"""
Module: settings_tk.py
Purpose:
  - Standalone Tkinter settings window (outside Pygame).
  - Mirrors Pygame settings logic: preset/custom grid sizes, AI difficulty, audio toggles.
  - Responsive layout with resize-debounce and PIL-backed background.
Future Hooks:
  - Synchronize changed settings across multiplayer peers.
"""

def _hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)

class SettingsTk:
    def __init__(self, state, on_back):
        # Initialize mixer to support sound effect toggling
        pygame.mixer.init()
        self.state   = state
        self.logic   = SettingsLogic(None, state)
        self.on_back = on_back

        # ─── Root window setup ────────────────────────────────────
        self.root = tk.Tk()
        self.root.title("Battleships Settings")
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        x = (sw - Config.WIDTH)//2
        y = (sh - Config.HEIGHT)//2
        self.root.geometry(f"{Config.WIDTH}x{Config.HEIGHT}+{x}+{y}")
        self.root.minsize(400, 300)

        # ─── Background canvas ───────────────────────────────────
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.orig_bg = Image.open("resources/images/cartoon_battle_bg.png")
        self._resize_bg(Config.WIDTH, Config.HEIGHT)

        # ─── Back button ──────────────────────────────────────────
        self.btn_back = tk.Button(
            self.root,
            text="← Back",
            bg=_hex(Config.GRAY), fg="white",
            activebackground=_hex(Config.DARK_GRAY),
            font=("Helvetica", 12, "bold"),
            command=self._on_back
        )

        # ─── Grid Size buttons ───────────────────────────────────
        self.grid_buttons = []
        for size in (5, 10, 15):
            b = tk.Button(
                self.root,
                text=f"{size}×{size}",
                fg="white",
                activebackground=_hex(Config.DARK_GRAY),
                font=("Helvetica", 12, "bold"),
                command=lambda s=size: self._apply_grid(s)
            )
            self.grid_buttons.append(b)

        # ─── AI Difficulty buttons ───────────────────────────────
        self.diff_buttons = []
        for lvl in Config.DIFFICULTIES:
            b = tk.Button(
                self.root,
                text=lvl,
                fg="white",
                activebackground=_hex(Config.DARK_GRAY),
                font=("Helvetica", 12, "bold"),
                command=lambda L=lvl: self._apply_diff(L)
            )
            self.diff_buttons.append(b)

        # ─── Sound Effects checkbox ─────────────────────────────
        self.sfx_var = tk.BooleanVar(value=self.state.sfxenabled)
        self.cb_sfx = tk.Checkbutton(
            self.root,
            text="Sound Effects",
            variable=self.sfx_var,
            command=self._on_sfx_toggle,
            bg=_hex(Config.GRAY), fg="white",
            selectcolor=_hex(Config.GRAY),
            activebackground=_hex(Config.DARK_GRAY),
            activeforeground="white"
        )

        # ─── Layout parameters ───────────────────────────────────
        self.back_geom = (0.02, 0.02, 0.15, 0.07)
        self.grid_row  = 0.25       # Row for grid buttons
        self.diff_row  = 0.55       # Pushed down for extra spacing
        self.sfx_row   = 0.75       # Lowered accordingly
        self.btn_w, self.btn_h = 0.20, 0.10
        self.spacing   = self.btn_w + 0.03

        # ─── Resize debounce & ESC ───────────────────────────────
        self.resize_job = None
        self.root.bind("<Configure>", self._debounce)
        self.root.bind("<Escape>", lambda e: self._on_back())

        # ─── Initial layout ──────────────────────────────────────
        self._layout()

    def _on_back(self):
        """Close window and invoke return callback."""
        self.root.destroy()
        self.on_back()

    def _apply_grid(self, size: int):
        """Apply a preset grid size and update layout."""
        self.logic.apply_grid_size(size)
        self._layout()

    def _apply_diff(self, level: str):
        self.logic.apply_difficulty(level)
        self._layout()

    def _on_sfx_toggle(self):
        # Preserve existing functionality: toggle state flag
        self.state.sfxenabled = self.sfx_var.get()

    def _debounce(self, event):
        if self.resize_job:
            self.root.after_cancel(self.resize_job)
        self.resize_job = self.root.after(100, self._layout)

    def _resize_bg(self, w: int, h: int):
        """Resize and draw background image to fill window."""
        img = self.orig_bg.resize((w, h), Image.LANCZOS)
        self.bg_img = ImageTk.PhotoImage(img)
        if hasattr(self, "_bg_id"):
            self.canvas.itemconfig(self._bg_id, image=self.bg_img)
        else:
            self._bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_img)
        self.canvas.image = self.bg_img

    def _layout(self):
        """Perform full layout of controls based on current window size."""
        w, h = self.root.winfo_width(), self.root.winfo_height()
        if w < 100 or h < 100:
            return

        # Redraw background to fill window
        self._resize_bg(w, h)

        # Place Back button at top-left
        bx, by, bw, bh = self.back_geom
        self.btn_back.place(relx=bx, rely=by, relwidth=bw, relheight=bh)

        # Calculate uniform font size for all controls
        btn_px = int(self.btn_w * w)
        labels = [b.cget("text") for b in self.grid_buttons + self.diff_buttons]
        labels.append("Sound Effects")
        longest = max(labels, key=len)
        max_sz = max(8, int(h * self.btn_h * 0.6))
        chosen = 8
        for sz in range(max_sz, 7, -1):
            f = tkFont.Font(family="Helvetica", size=sz, weight="bold")
            if f.measure(longest) <= btn_px * 0.85:
                chosen = sz
                break
        uniform = ("Helvetica", chosen, "bold")
        font_obj = tkFont.Font(family=uniform[0], size=uniform[1], weight=uniform[2])

        # Helper to draw labeled section with background rectangle
        def draw_label(text, y_rel, tag_base):
            # Remove old items
            self.canvas.delete(f"{tag_base}_bg")
            self.canvas.delete(f"{tag_base}_text")
            # Compute position
            x = w * 0.5
            y = h * y_rel
            # Measure text
            text_w = font_obj.measure(text)
            text_h = font_obj.metrics("linespace")
            pad = 8
            # Draw background rect
            self.canvas.create_rectangle(
                x - text_w/2 - pad,
                y - text_h/2 - pad,
                x + text_w/2 + pad,
                y + text_h/2 + pad,
                fill=_hex(Config.DARK_GRAY), outline="",
                tags=(f"{tag_base}_bg",)
            )
            # Draw text on top
            self.canvas.create_text(
                x, y,
                text=text,
                font=uniform,
                fill="white",
                tags=(f"{tag_base}_text",)
            )

        # ─── Grid Size section with background ───────────────────
        draw_label("Grid Size", self.grid_row - 0.08, "grid_label")
        mid_x = 0.5 - self.btn_w / 2
        for i, b in enumerate(self.grid_buttons):
            size = int(b.cget("text").split("×")[0])
            b.config(font=uniform,
                     bg=_hex(Config.GREEN if Config.GRID_SIZE == size else Config.GRAY))
            col = mid_x + (i - 1) * self.spacing
            b.place(relx=col, rely=self.grid_row, relwidth=self.btn_w, relheight=self.btn_h)

        # ─── AI Difficulty section with background (moved down) ──
        draw_label("AI Difficulty", self.diff_row - 0.08, "diff_label")
        for i, b in enumerate(self.diff_buttons):
            lvl = b.cget("text")
            b.config(font=uniform,
                     bg=_hex(Config.GREEN if self.state.difficulty == lvl else Config.GRAY))
            col = mid_x + (i - 1) * self.spacing
            b.place(relx=col, rely=self.diff_row, relwidth=self.btn_w, relheight=self.btn_h)

        # ─── Sound Effects checkbox ─────────────────────────────
        self.cb_sfx.config(font=uniform)
        self.cb_sfx.place(
            relx=0.5 - 0.15, rely=self.sfx_row,
            relwidth=0.3, relheight=0.08
        )

    def run(self):
        self.root.mainloop()
