import tkinter as tk
from ScrollBar import CustomScrollbar
from Theme import Theme
import threading
import queue
from ProgressBar import CustomProgressBar

class CustomTableView(tk.Frame):
    """A custom table view widget for displaying tabular data with support for themes and dataframes."""

    def __init__(self, master, columns=None, data=None,
                 row_height=10, column_width=100, truncate = None,
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
        self.theme = theme or getattr(master, 'theme', Theme("dark"))
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
        
        self.progress = CustomProgressBar(self, width=200)
        self.progress.grid(row=1, column=0, sticky="ew")
        self.progress.grid_remove()

        self.table_frame = tk.Frame(self.canvas, bg=self.theme.background)
        self.table_window = self.canvas.create_window((0, 0), window=self.table_frame, anchor="nw")

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.after_idle(self.after(50, self.build_table))

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

    def _process_render_queue(self):
        """Process the render queue and update the UI."""
        self.after(0,self.progress.grid)
        try:
            qsize = self.render_queue.qsize()
            rendered = 0
            while True:
                item_type, index, data = self.render_queue.get_nowait()
                if item_type == "header":
                    self.after(0, self._draw_header, index, data)
                elif item_type == "row":
                    self.after(0, self._draw_row, index, data)
                    self.after(0,self.canvas.configure(scrollregion=self.canvas.bbox("all")))
                rendered += 1
                self.progress.set_progress(rendered/qsize)
        except queue.Empty:
            self.after(0,self.progress.grid_remove)

    def _draw_header(self, col_index, col_name):
        """Draw a single column header."""
        header_bg = self.theme.border
        header_width = max([len(str(x[0])) for x in self.data]) if col_index == 0 else \
            max([len(str(x[col_index])) for x in self.data]) if self.autofit_columns else self.column_width // 10
        header_value = col_name[:self.truncate] if self.truncate is not None else col_name
        header = tk.Label(self.table_frame, text=header_value, bg=header_bg,
                          fg=self.theme.text, font=self.theme.font, justify=self.text_alignment,
                          width=header_width, height=1, padx=5, pady=5)
        header.grid(row=0, column=col_index, sticky='ew', padx=1, pady=1)

        header.bind("<Button-1>", lambda _, c=col_index: self._select_column(c))

    def _draw_row(self, row_index, row_data):
        """Draw a single row."""
        row_header_bg = self.theme.border
        row_height = max([x.count('\n') + 1 for x in row_data]) if self.autofit_rows else self.row_height // 10
        row_values = [str(x)[:self.truncate] for x in row_data[0]] if self.truncate is not None else row_data[0]
        row_header = tk.Label(self.table_frame, text=row_values, bg=row_header_bg,
                              fg=self.theme.text, font=self.theme.font, justify=self.text_alignment,
                              height=row_height, padx=5, pady=5)
        row_header.grid(row=row_index + 1, column=0, sticky="ew", padx=1, pady=1)
        row_header.bind("<Button-1>", lambda _, r=row_index: self._select_row(r))

        for col_index, cell_data in enumerate(row_data):
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
            self.selected_indices -= row_indices
            for col in range(len(self.columns)):
                if col == 0: continue
                widget = self.table_frame.grid_slaves(row=row + 1, column=col)[0]
                widget.config(bg=self.theme.widget_bg)
        else:
            self.selected_indices |= row_indices
            for col in range(len(self.columns)):
                if col == 0: continue
                widget = self.table_frame.grid_slaves(row=row + 1, column=col)[0]
                widget.config(bg=self.theme.focus)

    def _select_column(self, col):
        """Toggle selection of an entire column."""
        col_indices = {(row, col) for row in range(len(self.data))}
        
        if col_indices.issubset(self.selected_indices):
            if col == 0:
                col_indices = {(row, c) for row in range(len(self.data)) for c in range(len(self.columns))}
                self.selected_indices -= col_indices
                for row in range(len(self.data)):
                    for c in range(len(self.columns)):
                        widget = self.table_frame.grid_slaves(row=row + 1, column=min(c+1,len(self.columns)-1))[0]
                        widget.config(bg=self.theme.widget_bg)
            else:
                self.selected_indices -= col_indices
                for row in range(len(self.data)):
                    widget = self.table_frame.grid_slaves(row=row + 1, column=col)[0]
                    widget.config(bg=self.theme.widget_bg)
        else:
            if col == 0:
                col_indices = {(row, c) for row in range(len(self.data)) for c in range(len(self.columns))}
                self.selected_indices |= col_indices
                for row in range(len(self.data)):
                    for c in range(len(self.columns)):
                        widget = self.table_frame.grid_slaves(row=row + 1, column=min(c+1,len(self.columns)-1))[0]
                        widget.config(bg=self.theme.focus)
            else:
                self.selected_indices |= col_indices
                for row in range(len(self.data)):
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

if __name__ == "__main__":
    from Tk import Tk
    import pandas as pd

    root = Tk(theme_mode="dark")
    root.title("Custom TableView Demo")
    root.geometry("600x400")

    columns = [f'col {i}' for i in range(4)]
    index  = [f'row {i}' for i in range(20)]
    data = [[f'cell\n\n{c}' for c in columns] for i in index]
    dataframe = pd.DataFrame(data, columns=columns, index=index)

    table = CustomTableView(root,
                            columns=columns,
                            dataframe=dataframe,
                            column_width=150,
                            row_height=30,
                            theme=root.theme,
                            autofit_columns=True,
                            autofit_rows=False,
                            text_alignment='left')
    table.pack(fill="both", expand=True, padx=10, pady=10)

    def show_selected():
        print("Selected Indices:", table.get_selected_indices())

    from Button import CustomButton
    show_button = CustomButton(root, text="Show Selected", command=show_selected)
    show_button.pack(pady=10)

    root.mainloop() 