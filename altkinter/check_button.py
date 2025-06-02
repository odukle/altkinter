import tkinter as tk
from .theme import Theme 
from .altk import Tk
import cairo
from PIL import Image, ImageTk
from io import BytesIO

class CustomCheckButton(tk.Canvas):
    def __init__(self, master, text="", command=None, variable=None,
                 size=20, theme=None, **kwargs):

        self.root = master.winfo_toplevel() if hasattr(master, 'winfo_toplevel') else master
        self.theme = theme or self.root.theme if hasattr(self.root, 'theme') else Theme("light")
        parent_bg = master.cget("bg")

        super().__init__(master, width=size + 150, height=size + 4,
                         bg=parent_bg, highlightthickness=0, bd=0, **kwargs)

        self.command = command
        self.checked = variable if variable is not None else tk.BooleanVar(value=False)
        self.box_width = size
        self.box_height = size
        self.box_radius = size/5

        # Checkbox background (rounded, using cairo)
        self.box_image = self._create_rounded_box_image(
            size, size, self.box_radius,
            border_color=self.theme.border,
            bg_color=self.theme.widget_bg
        )
        self.box = self.create_image(2, 2, anchor="nw", image=self.box_image, tags="box")

        # Checkmark character (instead of line drawing)
        # Place checkmark exactly at the center of the checkbox box
        self.check = self.create_text(
            self.box_width / 2 + 1,
            self.box_height / 2 + 1,
            text="✅",
            font=(self.theme.font[0], size - size // 3),
            fill=self.theme.accent,
            state="hidden",
            tags="check"
        )

        # Label text
        self.label = self.create_text(size + 10, (size + 4) / 2,
                                      text=text,
                                      anchor="w",
                                      font=self.theme.font,
                                      fill=self.theme.text,
                                      tags="label")

        # Single click binding on the entire canvas
        self.tag_bind("box", "<Button-1>", self.toggle)
        self.tag_bind("label", "<Button-1>", self.toggle)
        self.bind("<Button-1>", self.toggle)

        self.update_check()

    def _create_rounded_box_image(self, width, height, radius, border_color, bg_color):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        ctx = cairo.Context(surface)

        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))

        border_rgb = hex_to_rgb(border_color)
        bg_rgb = hex_to_rgb(bg_color)

        # Draw border
        ctx.set_source_rgb(*border_rgb)
        self._rounded_rect(ctx, 0, 0, width, height, radius)
        ctx.fill()

        # Draw background (inset for border)
        ctx.set_source_rgb(*bg_rgb)
        self._rounded_rect(ctx, 1, 1, width-2, height-2, max(1, radius-1))
        ctx.fill()

        buffer = BytesIO()
        surface.write_to_png(buffer)
        buffer.seek(0)
        return ImageTk.PhotoImage(data=buffer.getvalue())

    def _rounded_rect(self, ctx, x, y, w, h, r):
        # Draw a rounded rectangle path on cairo context
        ctx.new_sub_path()
        ctx.arc(x + w - r, y + r, r, -0.5 * 3.1416, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, 0.5 * 3.1416)
        ctx.arc(x + r, y + h - r, r, 0.5 * 3.1416, 3.1416)
        ctx.arc(x + r, y + r, r, 3.1416, 1.5 * 3.1416)
        ctx.close_path()

    def toggle(self, event=None):
        # Prevent double-calling due to overlapping tags
        if event:
            event.widget.unbind("<Button-1>")

        current = self.checked.get()
        self.checked.set(not current)
        self.update_check()

        if self.command:
            self.command()

        self.after(50, lambda: self.bind("<Button-1>", self.toggle))  # Rebind after brief delay

    def update_check(self):
        # Update box image for checked/unchecked state
        if self.checked.get():
            fill = self.theme.active
        else:
            fill = self.theme.widget_bg

        self.box_image = self._create_rounded_box_image(
            self.box_width, self.box_height, self.box_radius,
            border_color=self.theme.border,
            bg_color=fill
        )
        self.itemconfig(self.box, image=self.box_image)

        if self.checked.get():
            self.itemconfig(self.check, state="normal")
        else:
            self.itemconfig(self.check, state="hidden")


if __name__ == "__main__":

    def on_toggle():
        print("Toggled!")

    app = Tk(theme_mode="dark")

    cb = CustomCheckButton(app, text="Enable Notifications", command=on_toggle)
    cb.pack(pady=20, padx=20)

    app.mainloop()

