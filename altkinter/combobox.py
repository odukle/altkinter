import tkinter as tk
from tkinter import StringVar
from .theme import Theme
from .listbox import CustomListBox
from .altk import Toplevel

class CustomComboBox(tk.Frame):
    def __init__(self, master, values=None, default=None, width=200, height=30,
                 border_radius=20, theme=None,dropdown_height=150, **kwargs):
        super().__init__(master, **kwargs)
        self.root = master.winfo_toplevel()
        self.theme = theme or self.root.theme if hasattr(self.root, 'theme') else Theme("light")
        self.values = values or []
        self.selected_value = StringVar(value=default or (self.values[0] if self.values else ""))
        self.width = width
        self.height = height
        self.border_radius = border_radius
        self.dropdown_window = None
        self.dropdown_height = dropdown_height
        

        # Configure the main frame
        self.configure(bg=self.theme.background)

        # Create the dropdown button
        self.dropdown_button = tk.Canvas(self, width=width, height=height,
                                          highlightthickness=0, bd=0, bg=self.theme.background)
        self.dropdown_button.pack(fill="x", expand=True)
        self.dropdown_button.bind("<Button-1>", self.toggle_dropdown)

        # Draw the border and background
        self.border_rect = self._create_rounded_rect(
            0, 0, width, height, border_radius,
            fill=self.theme.border, outline=""
        )
        self.bg_rect = self._create_rounded_rect(
            2, 2, width - 2, height - 2, border_radius - 2,
            fill=self.theme.widget_bg, outline=""
        )

        # Add the selected value text
        self.text_item = self.dropdown_button.create_text(
            10, height // 2, text=self.selected_value.get(),
            fill=self.theme.text, font=self.theme.font, anchor="w"
        )

        # Add the dropdown arrow using text
        self.arrow = self.dropdown_button.create_text(
            self.width - 15, self.height // 2, text="˅",
            fill=self.theme.text, font=self.theme.font, anchor="center"
        )

        # Bind the master window's configure event to update dropdown position
        self.root.bind("<Configure>", self.on_master_move)
        self.bind('<FocusIn>', lambda e: self.hide_dropdown())

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
        return self.dropdown_button.create_polygon(points, smooth=True, splinesteps=36, **kwargs)

    def toggle_dropdown(self, event=None):
        """Toggle the visibility of the dropdown menu."""
        if self.dropdown_window is None or not self.dropdown_window.winfo_exists():
            self.show_dropdown()
        else:
            self.hide_dropdown()

    def show_dropdown(self):
        """Show the dropdown menu as a Toplevel window."""
        self.dropdown_window = Toplevel(self)
        self.dropdown_window.overrideredirect(True)
        self.dropdown_window.configure(bg=self.theme.background)

        self.place_dropdown()
        
        # Add the CustomListBox to the dropdown
        self.listbox = CustomListBox(self.dropdown_window, items=self.values, width=self.width,
                                     height=self.dropdown_height, theme=self.theme)
        self.listbox.pack(fill="both", expand=True)
        self.listbox.listbox.bind("<<ListboxSelect>>", self.on_select)

        self.dropdown_button.itemconfig(self.arrow, text="˄")

    def place_dropdown(self):
        if self.dropdown_window is None or not self.dropdown_window.winfo_exists(): return
        """Place the dropdown menu below the combo box."""
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.height
        self.dropdown_window.geometry(f"{self.width}x{self.dropdown_height}+{x}+{y}")

    def hide_dropdown(self):
        """Hide the dropdown menu."""
        if self.dropdown_window:
            self.dropdown_window.destroy()
            self.dropdown_window = None
            self.dropdown_button.itemconfig(self.arrow, text="˅")

    def on_select(self, event):
        """Handle selection from the dropdown menu."""
        selected_items = self.listbox.get_selected_items()
        if selected_items:
            self.selected_value.set(selected_items[0])
            self.dropdown_button.itemconfig(self.text_item, text=selected_items[0])
        self.hide_dropdown()

    def get(self):
        """Get the currently selected value."""
        return self.selected_value.get()

    def set(self, value):
        """Set the selected value."""
        if value in self.values:
            self.selected_value.set(value)
            self.dropdown_button.itemconfig(self.text_item, text=value)

    def on_master_move(self, event):
        """Update the position of the dropdown when the master window moves."""
        if self.dropdown_window and self.dropdown_window.winfo_exists():
            self.place_dropdown()

if __name__ == "__main__":
    from .altk import Tk

    root = Tk(theme_mode="dark")
    root.title("Custom ComboBox Demo")
    root.geometry("400x300")

    def on_select():
        print("Selected Value:", combo.get())

    values = [f"Option {i}" for i in range(1, 10000)]
    combo = CustomComboBox(root, values=values, default="Option 1", theme=root.theme)
    combo.pack(pady=20)

    from .button import CustomButton
    select_button = CustomButton(root, text="Get Selected", command=on_select)
    select_button.pack(pady=10)

    root.mainloop()