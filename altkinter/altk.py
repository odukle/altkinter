import tkinter as tk
from .theme import Theme
from ctypes import windll, byref, sizeof, wintypes

class Tk(tk.Tk):
    def __init__(self, theme_mode="light"):
        super().__init__()
        self.theme = Theme(theme_mode)
        
        self.configure(bg=self.theme.background)
        self.after_idle(self.after,100,self.set_title_bar_color)  # Set title bar color after window is created
        
    def set_title_bar_color(self):
        """Set title bar color using Windows API"""
        hwnd = windll.user32.GetParent(self.winfo_id())
        color_value = wintypes.DWORD(int(self.theme.background.replace("#", "0x"), 16))
        try:
            DWMWA_CAPTION_COLOR = 35
            windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 
                DWMWA_CAPTION_COLOR, 
                byref(color_value), 
                sizeof(color_value)
            )
        except Exception as e:
            print(f"Title bar color change failed: {e}")
            
    def set_theme(self, mode):
        """Optional: Switch theme at runtime"""
        self.theme.set_mode(mode)
        self.configure(bg=self.theme.background)
        # Optionally, trigger updates on child widgets here if needed
        
    def destroy(self):
        # Make sure we destroy both windows
        if hasattr(self, 'taskbar_icon'):
            self.taskbar_icon.destroy()
        super().destroy()

class Toplevel(tk.Toplevel):
    def __init__(self, master=None, theme=None, **kwargs):
        super().__init__(master, **kwargs)
        self.theme = theme or getattr(master, 'theme', Theme("light"))
        self.configure(bg=self.theme.background)
        self.after_idle(self.after, 100, self.set_title_bar_color)

    def set_title_bar_color(self):
        """Set title bar color using Windows API"""
        hwnd = windll.user32.GetParent(self.winfo_id())
        color_value = wintypes.DWORD(int(self.theme.background.replace("#", "0x"), 16))
        try:
            DWMWA_CAPTION_COLOR = 35
            windll.dwmapi.DwmSetWindowAttribute(
                hwnd,
                DWMWA_CAPTION_COLOR,
                byref(color_value),
                sizeof(color_value)
            )
        except Exception as e:
            print(f"Title bar color change failed: {e}")

    def set_theme(self, mode):
        self.theme.set_mode(mode)
        self.configure(bg=self.theme.background)

class Frame(tk.Frame):
    def __init__(self, master=None, theme=None, **kwargs):
        self.theme = theme or getattr(master, 'theme', Theme("light"))
        bg = kwargs.pop("bg", self.theme.background)
        super().__init__(master, bg=bg, **kwargs)