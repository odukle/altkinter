import tkinter as tk
from .altk import Tk
from .theme import Theme

class CustomProgressBar(tk.Canvas):
    def __init__(self, master, width=200, height=10, progress=0.0,
                 bar_size=20, indeterminate=False, speed = 5, border_radius=10, theme=None, **kwargs):
        
        self.root = master.winfo_toplevel() if hasattr(master, 'winfo_toplevel') else master
        self.theme = theme or self.root.theme if hasattr(self.root, 'theme') else Theme("light")
        parent_bg = master.cget("bg")
        
        super().__init__(master, width=width, height=height,
                         highlightthickness=0, bd=0, bg=parent_bg, **kwargs)
        
        self._progress = progress
        self.bar_size = bar_size
        self.indeterminate = indeterminate
        self.border_radius = border_radius
        self.width = width
        self.height = height
        self.indet_pos = 0
        self.speed = min(10,max(1,speed))/1.5


        # Background and border
        self.border_rect = self._create_rounded_rect(
            0, 0, width, height,
            radius=border_radius,
            fill=self.theme.border,
            outline=""
        )

        # Progress rectangle
        self.progress_rect = self.create_rectangle(
            2, 2, (width - 2) * self._progress, height - 2,
            fill=self.theme.accent, width=0
        )

        if indeterminate:
            self._animate_indeterminate()

    def _create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, splinesteps=36, **kwargs)

    def set_progress(self, progress):
        """Set the progress value (0 to 1)."""
        self.indeterminate = False
        self._progress = max(0.0, min(1.0, progress))
        # Update the progress fill area
        self.coords(
            self.progress_rect,
            2, 2, (self.width - 2) * self._progress, self.height - 2
        )

    def _animate_indeterminate(self):
        """Animate the indeterminate progress bar."""
        if self.indeterminate:
            self.indet_pos = (self.indet_pos + self.bar_size // (self.bar_size/self.speed)) % (self.width + self.bar_size)
            pos_start = self.indet_pos - self.bar_size
            pos_end = self.indet_pos

            self.coords(
                self.progress_rect,
                max(2, pos_start), 2,
                min(pos_end, self.width - 2), self.height - 2
            )
            self.after(20, self._animate_indeterminate)

    def start_indeterminate(self):
        """Start the indeterminate animation."""
        if not self.indeterminate:
            self.indeterminate = True
            self._animate_indeterminate()

    def stop_indeterminate(self):
        """Stop the indeterminate animation."""
        self.indeterminate = False
        self.coords(
            self.progress_rect,
            2, 2, 2, self.height - 2  # Reset progress
        )

if __name__ == "__main__":
    root = Tk(theme_mode="dark")
    root.title("Custom ProgressBar Demo")
    pb_width = 200
    pb_height = 10
    bar_size = 30
    
    progressbar = CustomProgressBar(root, width=pb_width, height=pb_height, bar_size=bar_size, speed=5)
    progressbar.pack(padx=20, pady=20)
    
    def toggle_indeterminate():
        if not progressbar.indeterminate:
            progressbar.start_indeterminate()
        else:
            progressbar.stop_indeterminate()

    from .button import CustomButton
    indet_button = CustomButton(root, text="Toggle Indeterminate", command=toggle_indeterminate)
    indet_button.pack(pady=10)

    root.mainloop()