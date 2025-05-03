import tkinter as tk
from Theme import Theme 
from Tk import Tk

class CustomCheckButton(tk.Canvas):
    def __init__(self, master, text="", command=None, variable=None,
                 width=20, height=20, theme=None, **kwargs):

        self.theme = theme or getattr(master, 'theme', Theme("dark"))
        parent_bg = master.cget("bg")

        super().__init__(master, width=width + 150, height=height + 4,
                         bg=parent_bg, highlightthickness=0, bd=0, **kwargs)

        self.command = command
        self.checked = variable if variable is not None else tk.BooleanVar(value=False)

        # Checkbox background
        self.box = self.create_rectangle(2, 2, width, height,
                                         outline=self.theme.border,
                                         width=2,
                                         fill=self.theme.widget_bg,
                                         tags="box")

        # Checkmark character (instead of line drawing)
        self.check = self.create_text(width / 2, height / 2,
                                      text="✔",
                                      font=(self.theme.font[0], 12),
                                      fill=self.theme.accent,
                                      state="hidden",
                                      tags="check")

        # Label text
        self.label = self.create_text(width + 10, height / 2,
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
        if self.checked.get():
            self.itemconfig(self.check, state="normal")
            self.itemconfig(self.box, fill=self.theme.active)
        else:
            self.itemconfig(self.check, state="hidden")
            self.itemconfig(self.box, fill=self.theme.widget_bg)


if __name__ == "__main__":

    def on_toggle():
        print("Toggled!")

    app = Tk(theme_mode="dark")

    cb = CustomCheckButton(app, text="Enable Notifications", command=on_toggle)
    cb.pack(pady=20, padx=20)

    app.mainloop()

