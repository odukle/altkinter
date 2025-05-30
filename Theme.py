class Theme:
    def __init__(self, mode="dark"):
        self.set_mode(mode)

    def set_mode(self, mode):
        self.mode = mode
        self.font = ("Microsoft PhagsPa", 10)
        if mode == "dark":
            self.background = "#222222"
            self.widget_bg = "#2b2b2b"
            self.hover = "#3c3c3c"
            self.active = "#1a1a1a"
            self.accent = "#4da6ff"
            self.border = "#3c3c3c"
            self.focus = "#5e5e5e"
            self.text = "#ffffff"
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
        elif mode == "solarized-dark":
            self.background = "#002b36"
            self.widget_bg = "#003847"
            self.hover = "#405c63"
            self.active = "#00303a"
            self.accent = "#b58900"
            self.border = "#4a6a71"
            self.focus = "#56747b"
            self.text = "#ffffff"
            self.placeholder = "#3c5055"
        elif mode == "solarized-light":
            self.background = "#fdf6e3"
            self.widget_bg = "#f5e8d2"
            self.hover = "#d6cfc4"
            self.active = "#e9ddc7"
            self.accent = "#b58900"
            self.border = "#a8b0ad"
            self.focus = "#8a9997"
            self.text = "#657b83"
            self.placeholder = "#7a8a88"
        elif mode == "cyborg":
            self.background = "#060606"
            self.widget_bg = "#2a2a2a"
            self.hover = "#3e3e3e"
            self.active = "#1c1c1c"
            self.accent = "#2a9fd6"
            self.border = "#3e3e3e"
            self.focus = "#4e4e4e"
            self.text = "#ffffff"
            self.placeholder = "#6c757d"
        elif mode == "flatly":
            self.background = "#ecf0f1"
            self.widget_bg = "#ffffff"
            self.hover = "#d5d8dc"
            self.active = "#bdc3c7"
            self.accent = "#18bc9c"
            self.border = "#bdc3c7"
            self.focus = "#95a5a6"
            self.text = "#2c3e50"
            self.placeholder = "#7f8c8d"
        else:
            raise ValueError("Unsupported theme mode: choose 'dark', 'light', 'solarized-dark', 'solarized-light', 'cyborg', or 'flatly'")
