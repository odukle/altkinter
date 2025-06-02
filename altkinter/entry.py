import tkinter as tk
from PIL import Image, ImageTk
from .altk import Tk
from .theme import Theme
import cairo
from io import BytesIO

class CustomEntry(tk.Canvas):
    def __init__(self, master, width=200, height=30, border_radius=10,
                 placeholder_text="", theme=None, **kwargs):

        self.root = master.winfo_toplevel() if hasattr(master, 'winfo_toplevel') else master
        self.theme = theme or self.root.theme if hasattr(self.root, 'theme') else Theme("light")
        parent_bg = master.cget("bg")

        super().__init__(master, width=width, height=height,
                         highlightthickness=0, bd=0, bg=parent_bg, **kwargs)

        self.width = width
        self.height = height
        self.border_radius = border_radius
        self.placeholder_text = placeholder_text
        self.has_focus = False

        # Draw the rounded rectangle background using Cairo
        self.bg_image = self._create_rounded_entry_image(
            width, height, border_radius,
            border_color=self.theme.border,
            bg_color=self.theme.widget_bg
        )
        self.bg_image_id = self.create_image(0, 0, anchor="nw", image=self.bg_image)

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
        self.root.bind('<Button-1>', lambda e: self.root.focus() if e.widget != self.entry else None)   

    def _create_rounded_entry_image(self, width, height, radius, border_color, bg_color):
        # Convert hex to RGB
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))

        border_rgb = hex_to_rgb(border_color)
        bg_rgb = hex_to_rgb(bg_color)

        # Create Cairo surface
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        ctx = cairo.Context(surface)

        # Draw border
        ctx.set_source_rgb(*border_rgb)
        self._rounded_rect(ctx, 0, 0, width, height, radius)
        ctx.fill()

        # Draw background (inset for border)
        ctx.set_source_rgb(*bg_rgb)
        self._rounded_rect(ctx, 2, 2, width - 4, height - 4, radius - 2 if radius > 2 else radius)
        ctx.fill()

        # Convert to Tkinter image
        buffer = BytesIO()
        surface.write_to_png(buffer)
        buffer.seek(0)
        return ImageTk.PhotoImage(data=buffer.getvalue())

    def _rounded_rect(self, ctx, x, y, w, h, r):
        # Draw a rounded rectangle path on the Cairo context
        ctx.new_sub_path()
        ctx.arc(x + w - r, y + r, r, -1.57, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, 1.57)
        ctx.arc(x + r, y + h - r, r, 1.57, 3.14)
        ctx.arc(x + r, y + r, r, 3.14, 4.71)
        ctx.close_path()

    def on_focus_in(self, event):
        # Redraw with focus color
        self.bg_image = self._create_rounded_entry_image(
            self.width, self.height, self.border_radius,
            border_color=self.theme.focus,
            bg_color=self.theme.widget_bg
        )
        self.itemconfig(self.bg_image_id, image=self.bg_image)
        if self.placeholder_active:
            self.entry.delete(0, tk.END)
            self.entry.config(fg=self.theme.text)
            self.placeholder_active = False

    def on_focus_out(self, event):
        # Redraw with normal border
        self.bg_image = self._create_rounded_entry_image(
            self.width, self.height, self.border_radius,
            border_color=self.theme.border,
            bg_color=self.theme.widget_bg
        )
        self.itemconfig(self.bg_image_id, image=self.bg_image)
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
