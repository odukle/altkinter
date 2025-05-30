from progressbar import CustomProgressBar
from tkinter import Toplevel

class ProgressWindow:
    def __init__(self, master):

        top = Toplevel(master)
        top.overrideredirect(True)
        top.title("Loading...")
        
        # Center the popup in master
        top.update_idletasks()
        master_width = master.winfo_width()
        master_height = master.winfo_height()
        master_x = master.winfo_rootx()
        master_y = master.winfo_rooty()
        popup_width = 300
        popup_height = 50
        popup_x = master_x + (master_width - popup_width) // 2
        popup_y = master_y + (master_height - popup_height) // 2
        top.geometry(f"{popup_width}x{popup_height}+{popup_x}+{popup_y}")
        
        top.configure(bg=master.theme.background)
        top.transient(master)
        top.resizable(False, False)

        # Add the progress bar to the popup
        self.popup_progress = CustomProgressBar(top, width=250, theme=master.theme)
        self.popup_progress.pack(pady=20)
        self.window = top

    def set_progress(self, value):
        self.popup_progress.set_progress(value)

    def close_progress(self):
        self.window.destroy()

