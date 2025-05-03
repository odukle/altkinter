class Theme:
    def __init__(self, mode="dark"):
        self.set_mode(mode)

    def set_mode(self, mode):
        self.mode = mode
        self.font = ("Helvetica", 10)
        if mode == "dark":
            self.background = "#222222"
            self.widget_bg = "#2b2b2b"
            self.hover = "#3c3c3c"
            self.active = "#1a1a1a"
            self.accent = "#4da6ff"
            self.border = "#3c3c3c"
            self.focus = "#5e5e5e"
            self.text = "white"
            self.placeholder = "#777777"
        elif mode == "light":
            self.background = "#f0f0f0"
            self.widget_bg = "#ffffff"
            self.hover = "#e0e0e0"
            self.active = "#cccccc"
            self.accent = "#007aff"
            self.border = "#cccccc"
            self.focus = "#888888"
            self.text = "#000000"
            self.placeholder = "#aaaaaa"
        else:
            raise ValueError("Unsupported theme mode: choose 'dark' or 'light'")
