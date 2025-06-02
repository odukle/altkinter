import tkinter as tk
from .scrollbar import CustomScrollbar
from .theme import Theme

class CustomListBox(tk.Frame):
    def __init__(self, master, items=None, width=300, height=200,
                 multiselect=False, theme=None, **kwargs):
        
        self.root = master.winfo_toplevel() if hasattr(master, 'winfo_toplevel') else master
        self.theme = theme or self.root.theme if hasattr(self.root, 'theme') else Theme("light")

        super().__init__(master, width=width, height=height, bg=self.theme.widget_bg, **kwargs)

        self.items = items or []
        self.multiselect = multiselect

        # Configure frame dimensions
        self.configure(width=width, height=height)

        # Create a Listbox widget
        self.listvar = tk.StringVar(value=self.items)
        selectmode = "multiple" if multiselect else "browse"
        self.listbox = tk.Listbox(self, selectmode=selectmode, activestyle="none",
                                  bg=self.theme.widget_bg, fg=self.theme.text,
                                  font=self.theme.font, listvariable=self.listvar,
                                  highlightthickness=0, bd=0, relief="flat")
        self.listbox.pack(side="left", fill="both", expand=True, padx=10, pady=5)

        # Custom Scrollbar
        self.scrollbar = CustomScrollbar(self, command=self.listbox.yview, theme=self.theme)
        self.scrollbar.pack(side="right", fill="y")
        self.listbox.configure(yscrollcommand=self.scrollbar.set)

        # Bind hover events
        self.listbox.bind("<Motion>", self.on_hover)
        self.listbox.bind("<Leave>", self.on_leave)

        # Track the last hovered index
        self.last_hovered_index = None

    def on_hover(self, event):
        """Change the background of the item under the cursor."""
        index = self.listbox.nearest(event.y)
        if self.last_hovered_index is not None and self.last_hovered_index != index:
            # Reset the background of the previously hovered item
            self.listbox.itemconfig(self.last_hovered_index, bg=self.theme.widget_bg)
        # Highlight the current item
        self.listbox.itemconfig(index, bg=self.theme.hover)
        self.last_hovered_index = index

    def on_leave(self, event):
        """Reset the background when the cursor leaves the Listbox."""
        if self.last_hovered_index is not None:
            self.listbox.itemconfig(self.last_hovered_index, bg=self.theme.widget_bg)
            self.last_hovered_index = None

    def get_selected_items(self):
        """Return the selected items."""
        selected_indices = self.listbox.curselection()
        return [self.items[i] for i in selected_indices]

    def clear_selection(self):
        """Clear all selections."""
        self.listbox.selection_clear(0, "end")

    def select_item(self, index):
        """Select an item by index."""
        self.listbox.selection_set(index)

    def insert(self, index, item):
        """Add a new item to the Listbox."""
        self.items.append(item)
        self.listbox.insert(index, item)
        
    def set_items(self, items):
        """Set the items in the Listbox."""
        self.items = items
        self.listvar.set(items)

    def delete(self, first, last):
        """Remove items by index."""
        if 0 <= first <= last < len(self.items):
            [self.items.pop(i) for i in range(first, last + 1)]
            self.listbox.delete(first, last)


if __name__ == "__main__":
    from .altk import Tk

    root = Tk(theme_mode="dark")
    root.title("Custom ListBox Demo")
    root.geometry("400x500+500+200")

    items = [f"Item {i}" for i in range(1, 10000)]

    listbox = CustomListBox(root, items=items, width=300, height=300, multiselect=True, theme=root.theme)
    listbox.pack(padx=20, pady=20)

    def show_selected():
        print("Selected:", listbox.get_selected_items())

    from .button import CustomButton
    button = CustomButton(root, text="Get Selected Items", command=show_selected, width=150)
    button.pack(pady=10)

    root.mainloop()