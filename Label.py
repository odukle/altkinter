import tkinter as tk
from theme import Theme
from altk import Tk

class CustomLabel(tk.Label):
    def __init__(self, master, text="", font_size=12, font_weight="normal",
                 anchor="center", wraplength=None, theme=None, **kwargs):
        
        self.theme = theme or getattr(master, 'theme', Theme("dark"))

        font = (self.theme.font[0], font_size, font_weight)
        
        super().__init__(master,
                         text=text,
                         bg=self.theme.background,
                         fg=self.theme.text,
                         font=font,
                         anchor=anchor,
                         wraplength=wraplength,
                         **kwargs)
        
if __name__ == "__main__":
    root = Tk(theme_mode="dark")
    label = CustomLabel(root, text="Hello, Custom Label!", font_size=16, font_weight="bold")
    label.pack(pady=20)
    root.mainloop()
