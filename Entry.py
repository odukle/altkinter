import tkinter as tk
from Tk import Tk

class CustomEntry(tk.Canvas):
    def __init__(self, master, width=200, height=40, border_radius=20,
                 placeholder_text="", theme=None, **kwargs):

        self.theme = theme or master.theme
        parent_bg = master.cget("bg")

        super().__init__(master, width=width, height=height,
                         highlightthickness=0, bd=0, bg=parent_bg, **kwargs)

        self.border_radius = border_radius
        self.placeholder_text = placeholder_text
        self.has_focus = False

        # Background and border
        self.border_rect = self._create_rounded_rect(0, 0, width, height,
                                                     radius=border_radius,
                                                     fill=self.theme.border, outline="")
        self.inner_rect = self._create_rounded_rect(2, 2, width - 2, height - 2,
                                                    radius=border_radius - 2,
                                                    fill=self.theme.widget_bg, outline="")

        # Entry
        self.entry = tk.Entry(self, bd=0, highlightthickness=0,
                              bg=self.theme.widget_bg, fg=self.theme.text,
                              font=self.theme.font, insertbackground=self.theme.text)
        self.entry_window = self.create_window(width // 2, height // 2,
                                               window=self.entry,
                                               width=width - 16,
                                               height=height - 10)

        # Placeholder logic
        if placeholder_text:
            self.entry.insert(0, placeholder_text)
            self.entry.config(fg=self.theme.placeholder)
            self.placeholder_active = True
        else:
            self.placeholder_active = False

        self.entry.bind("<FocusIn>", self.on_focus_in)
        self.entry.bind("<FocusOut>", self.on_focus_out)

    def _create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, splinesteps=36, **kwargs)

    def on_focus_in(self, event):
        self.itemconfig(self.border_rect, fill=self.theme.focus)
        if self.placeholder_active:
            self.entry.delete(0, tk.END)
            self.entry.config(fg=self.theme.text)
            self.placeholder_active = False

    def on_focus_out(self, event):
        self.itemconfig(self.border_rect, fill=self.theme.border)
        if not self.entry.get() and self.placeholder_text:
            self.entry.insert(0, self.placeholder_text)
            self.entry.config(fg=self.theme.placeholder)
            self.placeholder_active = True

    def get(self):
        return "" if self.placeholder_active else self.entry.get()

    def set(self, text):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, text)
        self.entry.config(fg=self.theme.text)
        self.placeholder_active = False

if __name__ == "__main__":
    root = Tk(theme_mode="light")
    root.title("Custom Entry Demo")

    entry = CustomEntry(root,
                        placeholder_text="Enter text here...")
    entry.pack(padx=20, pady=20)

    def show_text():
        print("Entered:", entry.get())

    button = tk.Button(root, text="Print Entry", command=show_text)
    button.pack()

    root.mainloop()
