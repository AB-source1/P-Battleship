# screens/settings_tk.py

import tkinter as tk
from PIL import Image, ImageTk
from core.config import Config
from screens.settings_logic import SettingsLogic
import tkinter.font as tkFont

def rgb_to_hex(rgb: tuple[int,int,int]) -> str:
    """Convert an (R,G,B) tuple to a Tk-compatible hex string."""
    return "#{:02x}{:02x}{:02x}".format(*rgb)

class SettingsTk:
    def __init__(self, state, on_back):
        # ─── Save state & logic ─────────────────────────
        self.state = state
        self.logic = SettingsLogic(None, state)
        self.on_back = on_back

        # ─── Tear down any existing Tk root ─────────────────
        try:
            tk._default_root.destroy()
        except:
            pass

        # ─── Create our window ─────────────────────────────
        self.root = tk.Tk()
        self.root.title("Battleships Settings")

        # Center it
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        x = (sw - Config.WIDTH)//2
        y = (sh - Config.HEIGHT)//2
        self.root.geometry(f"{Config.WIDTH}x{Config.HEIGHT}+{x}+{y}")
        self.root.minsize(400, 300)
        self.root.configure(bg="black")

        # ─── Canvas + background ──────────────────────────
        self.canvas = tk.Canvas(self.root, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.orig_bg = Image.open("resources/images/cartoon_loading.png")
        self.bg_img   = ImageTk.PhotoImage(self.orig_bg.resize((Config.WIDTH, Config.HEIGHT), Image.LANCZOS))
        self.bg_id    = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_img)
        self.canvas.image = self.bg_img  # keep reference

        # ─── Build all widgets ────────────────────────────
        self._make_widgets()

        # ─── Bind resizing ─────────────────────────────────
        self.resize_job = None
        self.root.bind("<Configure>", self._debounce_resize)
        self.root.bind("<Escape>", lambda e: self._go_back())

        # ─── Initial layout & font scaling ─────────────────
        self._layout_and_scale()

    def _make_widgets(self):
        w = self.widgets = {}

        # Back
        w['back'] = tk.Button(self.root, text="Back", command=self._go_back)

        # Grid presets
        for size in (5, 10, 15):
            w[f"g{size}"] = tk.Button(
                self.root, text=f"{size}×{size}",
                command=lambda s=size: self._apply_grid(s)
            )

        # Custom
        w['custom'] = tk.Button(self.root, text="Custom", command=self._toggle_custom)
        w['entry']  = tk.Entry(self.root)
        w['apply']  = tk.Button(self.root, text="Apply", command=self._apply_custom)
        w['entry'].place_forget()
        w['apply'].place_forget()

        # Smart-placement toggle
        w['smart'] = tk.Button(self.root, text="", command=self._toggle_smart)

        # Difficulty
        for lvl in Config.DIFFICULTIES:
            w[f"d{lvl}"] = tk.Button(
                self.root, text=lvl,
                command=lambda L=lvl: self._apply_diff(L)
            )

    def _go_back(self):
        self.root.destroy()
        self.on_back()

    def _apply_grid(self, s:int):
        self.logic.apply_grid_size(s)
        self._layout_and_scale()

    def _toggle_custom(self):
        e,a = self.widgets['entry'], self.widgets['apply']
        if e.winfo_ismapped():
            e.place_forget(); a.place_forget()
        else:
            w,h = self.root.winfo_width(), self.root.winfo_height()
            e.place(x=w*0.35, y=h*0.4, width=w*0.3, height=30)
            a.place(x=w*0.7,  y=h*0.4, width=60,      height=30)

    def _apply_custom(self):
        self.logic.grid_size_input = self.widgets['entry'].get()
        self.logic.apply_custom_size()
        self._toggle_custom()
        self._layout_and_scale()

    def _toggle_smart(self):
        Config.USE_SMART_SHIP_GENERATOR = not Config.USE_SMART_SHIP_GENERATOR
        Config.generate_ships_for_grid()
        self._layout_and_scale()

    def _apply_diff(self, lvl:str):
        self.logic.apply_difficulty(lvl)
        self._layout_and_scale()

    def _debounce_resize(self, event):
        if self.resize_job:
            self.root.after_cancel(self.resize_job)
        self.resize_job = self.root.after(100, self._layout_and_scale)

    def _layout_and_scale(self):
        # Resize background
        w,h = self.root.winfo_width(), self.root.winfo_height()
        if w<100 or h<100: return

        bg = self.orig_bg.resize((w,h), Image.LANCZOS)
        self.bg_img = ImageTk.PhotoImage(bg)
        self.canvas.itemconfig(self.bg_id, image=self.bg_img)
        self.canvas.config(width=w, height=h)
        self.canvas.image = self.bg_img

        # Choose a uniform font size
        max_sz = max(8, int(h * 0.05))
        final = tkFont.Font(size=8, weight="bold")
        for sz in range(max_sz, 7, -1):
            f = tkFont.Font(size=sz, weight="bold")
            ok = True
            for key,widget in self.widgets.items():
                if isinstance(widget, tk.Button):
                    txt = widget.cget("text")
                    if f.measure(txt) > w * 0.4:
                        ok = False; break
            if ok:
                final = f
                break

        # Layout constants
        top = 20
        gap = final.metrics("linespace") + 10

        # Back
        b = self.widgets['back']
        b.config(font=final)
        b.place(x=10, y=top, width=80, height=gap)

        # Title text
        if not hasattr(self, 'title_id'):
            self.title_id = self.canvas.create_text(
                w/2, top + gap/2,
                text="Select Grid Size",
                fill="white",
                font=("Helvetica", max(16, int(h*0.04)), "bold")
            )
        else:
            self.canvas.coords(self.title_id, w/2, top + gap/2)

        # Grid presets
        for i, size in enumerate((5,10,15)):
            btn = self.widgets[f"g{size}"]
            raw = Config.GREEN if Config.GRID_SIZE==size else Config.GRAY
            btn.config(font=final, bg=rgb_to_hex(raw))
            btn.place(x=w*0.1 + i*(w*0.3+10), y=top+gap*2, width=w*0.3, height=gap)

        # Custom toggle
        cbtn = self.widgets['custom']
        cbtn.config(font=final, bg=rgb_to_hex(Config.GRAY))
        cbtn.place(x=w*0.35, y=top+gap*4, width=w*0.3, height=gap)

        # Smart-placement toggle
        sbtn = self.widgets['smart']
        label = "Smart: ON" if Config.USE_SMART_SHIP_GENERATOR else "Smart: OFF"
        raw   = Config.GREEN if Config.USE_SMART_SHIP_GENERATOR else Config.GRAY
        sbtn.config(text=label, font=final, bg=rgb_to_hex(raw))
        sbtn.place(x=w*0.7, y=top+gap*4, width=w*0.25, height=gap)

        # Difficulty buttons
        for i, lvl in enumerate(Config.DIFFICULTIES):
            dbtn = self.widgets[f"d{lvl}"]
            raw  = Config.GREEN if self.state.difficulty==lvl else Config.GRAY
            dbtn.config(font=final, bg=rgb_to_hex(raw))
            dbtn.place(x=w*0.1 + i*(w*0.3+10), y=top+gap*6, width=w*0.3, height=gap)

    def run(self):
        self.root.mainloop()
