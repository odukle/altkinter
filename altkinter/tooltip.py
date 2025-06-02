import tkinter as tk

class CanvasToolTip:
    def __init__(
        self,
        canvas,
        creation_id,
        text="widget info",
        wraplength=300,
        delay=250,
        **kwargs,
    ):
        self.canvas = canvas
        self.creation_id = creation_id
        self.text = text
        self.wraplength = wraplength
        self.toplevel = None
        self.delay = delay
        self.id = None

        kwargs["master"] = self.canvas
        self.toplevel_kwargs = kwargs

        self.canvas.tag_bind(self.creation_id, "<Enter>", self.enter)
        self.canvas.tag_bind(self.creation_id, "<Leave>", self.leave)
        self.canvas.tag_bind(self.creation_id, "<Motion>", self.move_tip)
        self.canvas.tag_bind(self.creation_id, "<ButtonPress>", self.leave)

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hide_tip()

    def schedule(self):
        self.unschedule()
        self.id = self.canvas.after(self.delay, self.show_tip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.canvas.after_cancel(id)

    def show_tip(self, *_):
        if self.toplevel:
            return
        x = self.canvas.winfo_pointerx() + 25
        y = self.canvas.winfo_pointery() + 10

        self.toplevel = tk.Toplevel(**self.toplevel_kwargs)
        self.toplevel.overrideredirect(True)
        lbl = tk.Label(
            master=self.toplevel,
            text=self.text,
            justify=tk.LEFT,
            wraplength=self.wraplength,
            bg="#fffddd",
            fg="#333",
            relief=tk.RAISED,
            bd=1,
            padx=10,
            pady=10,
        )
        lbl.pack(fill=tk.BOTH, expand=tk.YES)
        self.toplevel.geometry(f"+{x}+{y}")

    def move_tip(self, *_):
        if self.toplevel:
            x = self.canvas.winfo_pointerx() + 25
            y = self.canvas.winfo_pointery() + 10
            self.toplevel.geometry(f"+{x}+{y}")

    def hide_tip(self, *_):
        if self.toplevel:
            self.toplevel.destroy()
            self.toplevel = None


class ToolTip:
    def __init__(self, widget, text="widget info", wraplength=300, delay=250,
                 enter_binding = None, leave_binding = None,**kwargs):
        self.widget = widget
        self.text = text
        self.wraplength = wraplength
        self.toplevel = None
        self.delay = delay
        self.id = None
        self.enter_binding = enter_binding
        self.leave_binding = leave_binding

        kwargs["master"] = self.widget
        self.toplevel_kwargs = kwargs

        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<Motion>", self.move_tip)

    def enter(self, event=None):
        if self.enter_binding:
            # call the enter binding function
            self.enter_binding(event)
        self.schedule()

    def leave(self, event=None):
        if self.leave_binding:
            # call the leave binding function
            self.leave_binding(event)
        self.unschedule()
        self.hide_tip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.delay, self.show_tip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def show_tip(self, *_):
        if self.toplevel:
            return
        x = self.widget.winfo_pointerx() + 25
        y = self.widget.winfo_pointery() + 10

        self.toplevel = tk.Toplevel(**self.toplevel_kwargs)
        self.toplevel.overrideredirect(True)
        lbl = tk.Label(
            master=self.toplevel,
            text=self.text,
            justify=tk.LEFT,
            wraplength=self.wraplength,
            bg="#fffddd",
            fg="#333",
            relief=tk.RAISED,
            bd=1,
            padx=10,
            pady=10,
        )
        lbl.pack(fill=tk.BOTH, expand=tk.YES)
        self.toplevel.geometry(f"+{x}+{y}")

    def move_tip(self, *_):
        if self.toplevel:
            x = self.widget.winfo_pointerx() + 25
            y = self.widget.winfo_pointery() + 10
            self.toplevel.geometry(f"+{x}+{y}")

    def hide_tip(self, *_):
        if self.toplevel:
            self.toplevel.destroy()
            self.toplevel = None


if __name__ == "__main__":

    app = tk.Tk()
    app.title("Tooltip Example")
    canvas = tk.Canvas(app, width=400, height=300)
    canvas.pack(fill=tk.BOTH, expand=tk.YES)

    rect_id1 = canvas.create_rectangle(50, 50, 150, 100, fill="blue")
    rect_id2 = canvas.create_rectangle(200, 50, 300, 100, fill="red")
    CanvasToolTip(
        canvas,
        rect_id1,
        text="This is a blue rectangle",
    )
    CanvasToolTip(
        canvas,
        rect_id2,
        text="This is a red rectangle",
    )

    button = tk.Button(app, text="Hover over me")
    button.pack(pady=20)
    ToolTip(button, text="This is a button tooltip")

    app.mainloop()
