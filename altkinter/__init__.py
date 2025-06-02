"""
This file initializes the altkinter package and imports the necessary modules.

Available modules:
- CustomButton from button.py
- CustomCheckButton from check_button.py
- CustomComboBox from combobox.py
- CustomEntry from entry.py
- CustomLabel from label.py
- CustomListBox from listbox.py
- CustomProgressBar from progressbar.py
- CustomScrollbar from scrollbar.py
- CustomTableView from tableview.py
"""

from .button import CustomButton
from .check_button import CustomCheckButton
from .combobox import CustomComboBox
from .entry import CustomEntry
from .label import CustomLabel
from .listbox import CustomListBox
from .progressbar import CustomProgressBar
from .scrollbar import CustomScrollbar
from .tableview import CustomTableView
from .progress_window import ProgressWindow
from .theme import Theme
from .altk import Tk, Toplevel, Frame
from .tooltip import CanvasToolTip, ToolTip
__all__ = [
    "CustomButton",
    "CustomCheckButton",
    "CustomComboBox",
    "CustomEntry",
    "CustomLabel",
    "CustomListBox",
    "CustomProgressBar",
    "CustomScrollbar",
    "CustomTableView",
    "ProgressWindow",
    "Theme",
    "Tk",
    "Toplevel",
    "Frame",
    "CanvasToolTip",
    "ToolTip"
]

__version__ = "0.1.0"
__author__ = "Saurabh Odukle"
__email__ = "odukle@gmail.com"
__license__ = "MIT"