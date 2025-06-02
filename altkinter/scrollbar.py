import tkinter as tk
from .theme import Theme

class CustomScrollbar(tk.Canvas):
    def __init__(self, master, orient="vertical", command=None, theme=None, **kwargs):

        self.root = master.winfo_toplevel() if hasattr(master, 'winfo_toplevel') else master
        self.theme = theme or self.root.theme if hasattr(self.root, 'theme') else Theme("light")

        super().__init__(master, highlightthickness=0,
                        bg=(theme or self.theme).widget_bg, width=10 if orient == "vertical" else None,
                        height=None if orient == "vertical" else 10, **kwargs)

        self.orient = orient
        self.command = command
        self.thumb = None
        self.thumb_pos = (0, 0)
        self._scroll_func = None

        # Draw initial thumb
        self.bind("<Configure>", self._draw_thumb)
        self.bind("<Button-1>", self._click_thumb)
        self.bind("<B1-Motion>", self._drag_thumb)

    def set(self, lo, hi):
        """External call from widget to update thumb size/pos"""
        self.thumb_pos = (float(lo), float(hi))
        self._draw_thumb()

    def _draw_thumb(self, event=None):
        self.delete("thumb")

        lo, hi = self.thumb_pos
        if self.orient == "vertical":
            length = self.winfo_height()
            start = int(lo * length)
            end = int(hi * length)
            if end - start < 10:  # Ensure minimum thumb size
                end = start + 10
            self.thumb = self._draw_rounded_rect(
                2, start, 8, end, r=4,
                fill=self.theme.focus,
                width=0,
                tags="thumb"
            )
        else:  # horizontal
            length = self.winfo_width()
            start = int(lo * length)
            end = int(hi * length)
            if end - start < 5:  # Ensure minimum thumb size
                end = start + 5
            self.thumb = self._draw_rounded_rect(
                start, 2, end, 8, r=4,
                fill=self.theme.focus,
                width=0,
                tags="thumb"
            )

    def _draw_rounded_rect(self, x1, y1, x2, y2, r=4, **kwargs):
        """Draw a rounded rectangle on the canvas"""
        points = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, splinesteps=36, **kwargs)

    def _click_thumb(self, event):
        self._drag_start = event.y if self.orient == "vertical" else event.x
        self._start_lo, self._start_hi = self.thumb_pos

    def _drag_thumb(self, event):
        drag_pos = event.y if self.orient == "vertical" else event.x
        delta = (drag_pos - self._drag_start) / (self.winfo_height() if self.orient == "vertical" else self.winfo_width())

        new_lo = self._start_lo + delta
        new_hi = self._start_hi + delta

        thumb_size = self._start_hi - self._start_lo

        # Clamp low bound
        if new_lo < 0.0:
            new_lo = 0.0
            new_hi = new_lo + thumb_size

        # Clamp high bound
        if new_hi > 1.0:
            new_hi = 1.0
            new_lo = new_hi - thumb_size

        self.set(new_lo, new_hi)
        if self.command:
            self.command("moveto", new_lo)