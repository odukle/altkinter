import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

import tkinter as tk
from altkinter.altk import Tk, Frame
from altkinter.button import CustomButton
from altkinter.label import CustomLabel
from altkinter.entry import CustomEntry
from altkinter.progressbar import CustomProgressBar
from altkinter.listbox import CustomListBox
from altkinter.combobox import CustomComboBox
from altkinter.check_button import CustomCheckButton
from altkinter.scrollbar import CustomScrollbar
from altkinter.tableview import CustomTableView

class SampleApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Custom Widgets Showcase")
        
        self.frame = Frame(master)
        self.frame.pack(padx=20, pady=20)

        # Custom Label
        self.label = CustomLabel(self.frame, text="Welcome to the Custom Widgets Showcase!", font_size=16, font_weight="bold")
        self.label.pack(pady=10)

        # Entry and Button side by side
        entry_button_frame = Frame(self.frame)
        entry_button_frame.pack(pady=10)
        self.entry = CustomEntry(entry_button_frame, placeholder_text="Enter some text...")
        self.entry.pack(side="left", padx=(0, 10))
        self.button = CustomButton(entry_button_frame, text="Click Me", command=self.on_button_click)
        self.button.pack(side="left")

        # Progress Bar
        self.progress_bar = CustomProgressBar(self.frame, width=200, height=10)
        self.progress_bar.pack(pady=10)
        self.master.after(50, self.progress_bar.start_indeterminate)

        # ListBox and TableView side by side
        list_table_frame = Frame(self.frame)
        list_table_frame.pack(pady=10, fill="both", expand=True)
        self.listbox = CustomListBox(list_table_frame, items=[f"Item {i}" for i in range(1, 21)], multiselect=True)
        self.listbox.pack(side="left", padx=(0, 10), fill="y")
        columns = [f'Column {i}' for i in range(5)]
        data = [[f'Row {r} Col {c}' for c in range(5)] for r in range(10)]
        self.table_view = CustomTableView(list_table_frame, columns=columns, data=data, row_height=10, column_width=100)
        self.table_view.pack(side="left", fill="both", expand=True)

        # ComboBox and CheckButton side by side
        combo_check_frame = Frame(self.frame)
        combo_check_frame.pack(pady=10)
        self.combo = CustomComboBox(combo_check_frame, values=[f"Option {i}" for i in range(1, 21)], default="Option 1")
        self.combo.pack(side="left", padx=(0, 10))
        self.check_button = CustomCheckButton(combo_check_frame, text="Enable Notifications", command=self.on_check_button_toggle)
        self.check_button.pack(side="left")

    def on_button_click(self):
        print("Button clicked!")
        self.progress_bar.set_progress(0.5)

    def on_check_button_toggle(self):
        print("Check button toggled!")

if __name__ == "__main__":
    root = Tk(theme_mode="dark")
    app = SampleApp(root)
    root.mainloop()
