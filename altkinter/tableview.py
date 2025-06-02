import tkinter as tk
from .scrollbar import CustomScrollbar
from .theme import Theme
import threading
import queue
from .progressbar import CustomProgressBar
from .progress_window import *
from .tooltip import ToolTip

class CustomTableView(tk.Frame):
    """A custom table view widget for displaying tabular data with support for themes and dataframes."""

    def __init__(self, master, columns=None, data=None, row_height=10,
                 column_width=100, truncate = None, tooltip = 'on',
                 autofit_columns=False, autofit_rows = False,
                 theme=None, dataframe=None, text_alignment='left',
                 *args, **kwargs):
        """
        Initialize the table view with columns, data, styling, and optional dataframe.

        :param master: The parent widget.
        :param columns: A list of column names.
        :param data: A list of data rows.
        :param row_height: The height of each row in pixels.
        :param column_width: The width of each column in pixels.
        :param autofit: Boolean to enable column width auto-fitting based on content.
        :param theme: The theme style to apply.
        :param dataframe: Optional pandas DataFrame to populate the table with.
        :param text_alignment: Text alignment for table cells ('w', 'e', 'center').

        Accepts all tk.Frame arguments: background, bd, bg, borderwidth, class,
        colormap, container, cursor, height, highlightbackground,
        highlightcolor, highlightthickness, relief, takefocus, visual, width.
        """

        self.root = master.winfo_toplevel() if hasattr(master, 'winfo_toplevel') else master
        self.theme = theme or self.root.theme if hasattr(self.root, 'theme') else Theme("light")
        super().__init__(master, bg=self.theme.background, *args, **kwargs)

        self.columns = columns or []
        self.data = data or []
        self.autofit_columns = autofit_columns
        self.autofit_rows = autofit_rows
        self.dataframe = dataframe
        self.row_height = row_height
        self.column_width = column_width
        self.selected_cell = None
        self.selected_indices = set()
        self.render_queue = queue.Queue()
        self.text_alignment = text_alignment
        self.truncate = truncate
        self.master = master
        self.tooltip = tooltip
        self.progress_window = None

        if dataframe is not None:
            pass
            self.columns = [""] + list(dataframe.columns)
            self.data = dataframe.reset_index().values.tolist()
        else:
            self.columns = [""] + self.columns
            self.data = [[i + 1] + row for i, row in enumerate(self.data)]

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.canvas = tk.Canvas(self, bg=self.theme.background, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        self.scrollbar_v = CustomScrollbar(self, command=self.canvas.yview, theme=self.theme)
        self.scrollbar_v.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=self.scrollbar_v.set)
        
        self.scrollvar_h = CustomScrollbar(self, orient="horizontal", command=self.canvas.xview, theme=self.theme)
        self.scrollvar_h.grid(row=1, column=0, sticky="ew")
        self.canvas.configure(xscrollcommand=self.scrollvar_h.set)

        self.table_frame = tk.Frame(self.canvas, bg=self.theme.background)
        self.table_window = self.canvas.create_window((0, 0), window=self.table_frame, anchor="nw")

        # Bind mouse wheel only when mouse is over the canvas
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

        self.after_idle(self.after(50, self.build_table))
        self.master.bind("<Configure>", self.on_master_move)

    def _bind_mousewheel(self, event=None):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, event=None):
        self.canvas.unbind_all("<MouseWheel>")

    def build_table(self):
        """Start rendering the table in a separate thread."""
        thread =  threading.Thread(target=self._build_table_data, daemon=True)
        thread.start()
        threading.Thread(target=self._process_render_queue, daemon=True).start()
        
    def _build_table_data(self):
        """Build the table headers and rows in a separate thread."""
        for col_index, col_name in enumerate(self.columns):
            self.render_queue.put(("header", col_index, col_name))

        for row_index, row_data in enumerate(self.data):
            self.render_queue.put(("row", row_index, row_data))

    def _process_render_queue(self, batch_size=50):
        """Process the render queue and update the UI in batches."""
        self.progress_window = ProgressWindow(self.master)
        total_items = self.render_queue.qsize()
        rendered = 0

        def process_batch():
            nonlocal rendered
            while not self.render_queue.empty():
                try:
                    for _ in range(batch_size):
                        if self.render_queue.empty():
                            self.progress_window.close_progress()
                            self.progress_window = None
                            break
                        item_type, index, data = self.render_queue.get_nowait()
                        if item_type == "header":
                            self._draw_header(index, data)
                        elif item_type == "row":
                            self._draw_row(index, data)
                        rendered += 1
                        self.progress_window.set_progress(rendered / total_items)

                    # Update scrollregion after each batch
                    self.after(10, lambda: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

                    # Schedule the next batch if there are more items
                    if not self.render_queue.empty():
                        self.after(10, process_batch)
                        return
                except queue.Empty:
                    self.after(10, lambda: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
                    break
                

        # Start processing the first batch
        process_batch()

    def _draw_header(self, col_index, col_name):
        """Draw a single column header."""
        header_bg = self.theme.border
        header_value = col_name[:self.truncate] if self.truncate is not None else col_name
      
        if self.truncate is not None:
            header_width = max([len(str(x[0])[:self.truncate]) for x in self.data]) if col_index == 0 else \
                max([len(str(x[col_index])[:self.truncate]) for x in self.data]) if self.autofit_columns else self.column_width // 10
        else:
            header_width = max([len(str(x[0])) for x in self.data]) if col_index == 0 else \
            max([len(str(x[col_index])) for x in self.data]) if self.autofit_columns else self.column_width // 10

        header = tk.Label(self.table_frame, text=header_value, bg=header_bg,
                          fg=self.theme.text, font=self.theme.font, justify=self.text_alignment,
                          width=header_width, height=1, padx=5, pady=5)
        header.grid(row=0, column=col_index, sticky='ew', padx=1, pady=1)
        header.bind("<Button-1>", lambda _, c=col_index: self._select_column(c))

        if self.tooltip == 'on':
            ToolTip(header, text=str(col_name), wraplength=300)
        

    def _draw_row(self, row_index, row_data):
        """Draw a single row."""
        row_header_bg = self.theme.border
        row_height = max([x.count('\n') + 1 for x in row_data]) if self.autofit_rows else self.row_height // 10
        row_values = [str(x)[:self.truncate] for x in row_data] if self.truncate is not None else row_data
        row_header = tk.Label(self.table_frame, text=row_values[0], bg=row_header_bg,
                              fg=self.theme.text, font=self.theme.font, justify=self.text_alignment,
                              height=row_height, padx=5, pady=5)
        row_header.grid(row=row_index + 1, column=0, sticky="ew", padx=1, pady=1)
        row_header.bind("<Button-1>", lambda _, r=row_index: self._select_row(r))
        if self.tooltip:
            ToolTip(row_header,text=row_data[0], wraplength=300)

        for col_index, cell_data in enumerate(row_values):
            if col_index == 0:
                continue
            cell_bg = self.theme.widget_bg
            cell = tk.Label(self.table_frame, text=cell_data, bg=cell_bg,
                            fg=self.theme.text, font=self.theme.font, justify=self.text_alignment,
                            height=1, padx=5, pady=5)
            cell.grid(row=row_index + 1, column=col_index, sticky="nsew", padx=1, pady=1)

            cell.bind("<Enter>", lambda e, r=row_index, c=col_index: self._on_cell_hover(e, r, c))
            cell.bind("<Leave>", lambda e, r=row_index, c=col_index: self._on_cell_leave(e, r, c))
            cell.bind("<Button-1>", lambda e, r=row_index, c=col_index: self._on_cell_click(e, r, c))

            if self.tooltip == 'on':
                ToolTip(cell, text=str(row_data[col_index]), wraplength=300,
                        enter_binding=lambda e, r=row_index, c=col_index: self._on_cell_hover(e, r, c),
                        leave_binding=lambda e, r=row_index, c=col_index: self._on_cell_leave(e, r, c))

    def _on_mousewheel(self, event):
        """Scroll the canvas on mouse wheel."""
        if event.state & 0x0001 or event.state & 0x0004:
            self.canvas.xview_scroll(-1 * (event.delta // 120), "units")
        else:
            self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def _on_cell_hover(self, event, *_):
        """Change cell background color on hover."""
        event.widget.config(bg=self.theme.hover)

    def _on_cell_leave(self, event, row, col):
        """Revert cell background color when hover ends."""
        if (row, col) not in self.selected_indices:
            event.widget.config(bg=self.theme.widget_bg)
        else:
            event.widget.config(bg=self.theme.focus)

    def _on_cell_click(self, event, row, col):
        """Indicate the selected cell."""
        if (row, col) in self.selected_indices and col > 0:
            self.selected_indices.remove((row, col))
            event.widget.config(bg=self.theme.widget_bg)
        elif col > 0:
            self.selected_indices.add((row, col))
            event.widget.config(bg=self.theme.focus)

    def _select_row(self, row):
        """Toggle selection of an entire row."""
        row_indices = {(row, col) for col in range(len(self.columns)) if col != 0}
        if row_indices.issubset(self.selected_indices):
            # Deselect the row
            self.selected_indices -= row_indices
            for col in range(1, len(self.columns)):
                widget = self.table_frame.grid_slaves(row=row + 1, column=col)[0]
                widget.config(bg=self.theme.widget_bg)
        else:
            # Select the row
            self.selected_indices |= row_indices
            for col in range(1, len(self.columns)):
                widget = self.table_frame.grid_slaves(row=row + 1, column=col)[0]
                widget.config(bg=self.theme.focus)

    def _select_column(self, col):
        """Toggle selection of an entire column."""
        col_indices = {(row, col) for row in range(len(self.data))}
        if col_indices.issubset(self.selected_indices):
            # Deselect the column
            self.selected_indices -= col_indices
            for row in range(len(self.data)):
                widget = self.table_frame.grid_slaves(row=row + 1, column=col)[0]
                widget.config(bg=self.theme.widget_bg)
        else:
            # Select the column
            if col == 0:
                self._select_all()
                return
            self.selected_indices |= col_indices
            for row in range(len(self.data)):
                widget = self.table_frame.grid_slaves(row=row + 1, column=col)[0]
                widget.config(bg=self.theme.focus)

    def _select_all(self):
        """Toggle selection of all cells."""
        all_indices = {(row, col) for row in range(len(self.data)) for col in range(1, len(self.columns))}
        if all_indices.issubset(self.selected_indices):
            # Deselect all cells
            self.selected_indices.clear()
            for row in range(len(self.data)):
                for col in range(1, len(self.columns)):
                    widget = self.table_frame.grid_slaves(row=row + 1, column=col)[0]
                    widget.config(bg=self.theme.widget_bg)
        else:
            # Select all cells
            self.selected_indices = all_indices
            for row in range(len(self.data)):
                for col in range(1, len(self.columns)):
                    widget = self.table_frame.grid_slaves(row=row + 1, column=col)[0]
                    widget.config(bg=self.theme.focus)

    def get_selected_indices(self):
        """Return the indices of selected cells."""
        selected_indices = {(row, col-1) for row, col in self.selected_indices if col > 0}
        return selected_indices

    def set_data(self, data):
        """Update the table data and redraw."""
        self.data = [[i + 1] + row for i, row in enumerate(data)]
        self._draw_table()
        
    def set_columns(self, columns):
        """Set new column names and redraw the table."""
        self.columns = [""] + columns
        self._draw_table()
        
    def set_dataframe_from_csv(self, csv_file):
        """Set a pandas DataFrame from a CSV file as the table data."""
        import pandas as pd
        dataframe = pd.read_csv(csv_file)
        self.set_dataframe(dataframe)
        
    def get_column_headers(self):
        """Return the current column names."""
        return self.columns[1:]

    def get_data(self):
        """Return the current table data."""
        return [row[1:] for row in self.data]
    
    def get_row_headers(self):
        """Return the current row names."""
        return [row[0] for row in self.data]
    
    def set_dataframe(self, dataframe):
        """Set a pandas DataFrame as the table data."""
        self.columns = [""] + list(dataframe.columns)
        self.data = dataframe.reset_index().values.tolist()
        self._draw_table()

    def add_row(self, row_data):
        """Add a new row to the table."""
        self.data.append([len(self.data) + 1] + row_data)
        self._draw_table()

    def clear_data(self):
        """Clear all table data."""
        self.data = []
        self._draw_table()

    def on_master_move(self, event):
        """Update the position of the progress windoe when the master window moves."""
        if not self.progress_window or not self.progress_window.window.winfo_exists(): return
        self.progress_window.window.update_idletasks()
        master_width = self.master.winfo_width()
        master_height = self.master.winfo_height()
        master_x = self.master.winfo_rootx()
        master_y = self.master.winfo_rooty()
        popup_width = 300
        popup_height = 50
        popup_x = master_x + (master_width - popup_width) // 2
        popup_y = master_y + (master_height - popup_height) // 2
        self.progress_window.window.geometry(f"{popup_width}x{popup_height}+{popup_x}+{popup_y}")
        
if __name__ == "__main__":
    from .altk import Tk
    import pandas as pd

    root = Tk(theme_mode="solarized-dark")
    root.title("Custom TableView Demo")
    root.geometry("600x400")

    columns = [f'col {i}' for i in range(10)]
    index  = [f'row {i}' for i in range(100)]
    data = [[f'cell_{(r)*len(columns) + c+1}' for c in range(len(columns))] for r in range(len(index))]
    dataframe = pd.DataFrame(data, columns=columns, index=index)

    table = CustomTableView(root,
                            columns=columns,    
                            dataframe=dataframe,
                            column_width=150,
                            row_height=10,
                            theme=root.theme,
                            autofit_columns=True,
                            autofit_rows=True,
                            text_alignment='left')
    table.pack(fill="both", expand=True, padx=10, pady=10)

    def show_selected():
        print("Selected Indices:", table.get_selected_indices())

    from .button import CustomButton
    show_button = CustomButton(root, text="Show Selected", command=show_selected)
    show_button.pack(pady=10)

    root.mainloop()