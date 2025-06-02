import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
from .theme import Theme
from .altk import Tk
import cairo
from io import BytesIO

class CustomButton(tk.Label):
    def __init__(self, master, text="", command=None, width=100, height=30,
                 border_radius=10, theme=None, **kwargs):
        
        self.root = master.winfo_toplevel() if hasattr(master, 'winfo_toplevel') else master
        self.theme = theme or self.root.theme if hasattr(self.root, 'theme') else Theme("light")
        parent_bg = master.cget("bg")

        self.width = width
        self.height = height
        self.border_radius = border_radius
        self.command = command
        self.text = text

        # Create the button image with rounded corners
        self.image = self._create_rounded_button_image(
            width, height, border_radius,
            border_color=self.theme.border,
            bg_color=self.theme.widget_bg,
            text_color=self.theme.text,
            text=text,
            font=self.theme.font
        )

        # Initialize the Label widget with the image
        super().__init__(master, image=self.image, bg=parent_bg, **kwargs)

        # Bind interaction events
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<ButtonPress-1>", self.on_click)
        self.bind("<ButtonRelease-1>", self.on_release)


    def _create_rounded_button_image(self, width, height, radius, border_color, bg_color, text_color, text, font):
        # Create a blank image with cairo
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        context = cairo.Context(surface)

        # Convert colors from hex to RGB
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))

        border_rgb = hex_to_rgb(border_color)
        bg_rgb = hex_to_rgb(bg_color)
        text_rgb = hex_to_rgb(text_color)

        # Draw the border
        context.set_source_rgb(*border_rgb)
        context.arc(radius, radius, radius, 3.14, 1.5 * 3.14)
        context.arc(width - radius, radius, radius, 1.5 * 3.14, 0)
        context.arc(width - radius, height - radius, radius, 0, 0.5 * 3.14)
        context.arc(radius, height - radius, radius, 0.5 * 3.14, 3.14)
        context.close_path()
        context.fill()

        # Draw the background (inset slightly for the border)
        context.set_source_rgb(*bg_rgb)
        context.arc(radius + 1, radius + 1, radius - 1, 3.14, 1.5 * 3.14)
        context.arc(width - radius - 1, radius + 1, radius - 1, 1.5 * 3.14, 0)
        context.arc(width - radius - 1, height - radius - 1, radius - 1, 0, 0.5 * 3.14)
        context.arc(radius + 1, height - radius - 1, radius - 1, 0.5 * 3.14, 3.14)
        context.close_path()
        context.fill()

        # Load the font
        context.select_font_face(font[0], cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        context.set_font_size(font[1] * 1.2)

        # Calculate text position
        text_extents = context.text_extents(text)
        text_x = (width - text_extents.width) / 2 - text_extents.x_bearing
        text_y = (height - text_extents.height) / 2 - text_extents.y_bearing * 1.1

        # Draw the text
        context.set_source_rgb(*text_rgb)
        context.move_to(text_x, text_y)
        context.show_text(text)

        # Save the cairo surface to a BytesIO object in PNG format
        buffer = BytesIO()
        surface.write_to_png(buffer)
        buffer.seek(0)

        # Load the PNG data into a Tkinter-compatible image
        return ImageTk.PhotoImage(data=buffer.getvalue())


    def on_enter(self, event):
        self.image = self._create_rounded_button_image(
            self.width, self.height, self.border_radius,
            border_color=self.theme.border,
            bg_color=self.theme.hover,
            text_color=self.theme.text,
            text=self.text,
            font=self.theme.font
        )
        self.config(image=self.image)

    def on_leave(self, event):
        self.image = self._create_rounded_button_image(
            self.width, self.height, self.border_radius,
            border_color=self.theme.border,
            bg_color=self.theme.widget_bg,
            text_color=self.theme.text,
            text=self.text,
            font=self.theme.font
        )
        self.config(image=self.image)

    def on_click(self, event):
        self.image = self._create_rounded_button_image(
            self.width, self.height, self.border_radius,
            border_color=self.theme.border,
            bg_color=self.theme.active,
            text_color=self.theme.text,
            text=self.text,
            font=self.theme.font
        )
        self.config(image=self.image)

    def on_release(self, event):
        self.image = self._create_rounded_button_image(
            self.width, self.height, self.border_radius,
            border_color=self.theme.border,
            bg_color=self.theme.hover,
            text_color=self.theme.text,
            text=self.text,
            font=self.theme.font
        )
        self.config(image=self.image)
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
