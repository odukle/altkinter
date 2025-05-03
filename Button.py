import tkinter as tk
from Theme import Theme
from Tk import Tk

class CustomButton(tk.Canvas):
    def __init__(self, master, text="", command=None, width=100, height=30,
                 border_radius=20, theme=None, **kwargs):

        self.theme = theme or master.theme
        parent_bg = master.cget("bg")

        super().__init__(master, width=width, height=height,
                         highlightthickness=0, bd=0, bg=parent_bg, **kwargs)

        self.command = command
        self.text = text
        self.width = width
        self.height = height
        self.border_radius = border_radius

        # Border layer (slightly larger)
        self.border_rect = self._create_rounded_rect(
            0, 0, width, height, border_radius,
            fill=self.theme.border, outline=""
        )

        # Background layer (slightly inset)
        self.bg_rect = self._create_rounded_rect(
            2, 2, width - 2, height - 2, border_radius - 2,
            fill=self.theme.widget_bg, outline=""
        )

        self.text_item = self.create_text(
            width / 2, height / 2, text=text,
            fill=self.theme.text, font=self.theme.font
        )

        # Bind interaction events
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<ButtonPress-1>", self.on_click)
        self.bind("<ButtonRelease-1>", self.on_release)

    def _create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
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
        return self.create_polygon(points, smooth=True, splinesteps=100, **kwargs)

    def on_enter(self, event):
        self.itemconfig(self.bg_rect, fill=self.theme.hover)

    def on_leave(self, event):
        self.itemconfig(self.bg_rect, fill=self.theme.widget_bg)

    def on_click(self, event):
        self.itemconfig(self.bg_rect, fill=self.theme.active)

    def on_release(self, event):
        self.itemconfig(self.bg_rect, fill=self.theme.hover)
        if self.command:
            self.command()


if __name__ == "__main__":
    root = Tk(theme_mode="dark")
    root.title("Custom Button Demo")
    
    def on_button_click():
        print("Button clicked!")
    
    btn = CustomButton(root, text="Click Me", command=on_button_click)
    btn.pack(padx=20, pady=20)

    root.mainloop()
