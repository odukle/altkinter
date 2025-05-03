import tkinter as tk
from ScrollBar import CustomScrollbar
from Theme import Theme
import threading
import queue


class CustomTableView(tk.Frame):
    def __init__(self, master, columns=None, data=None, row_height=30, column_width=100, autofit=False,
                 theme=None, dataframe=None, **kwargs):
        self.theme = theme or getattr(master, 'theme', Theme("dark"))
        super().__init__(master, bg=self.theme.background, **kwargs)

        self._columns = columns or []
        self._data = data or []
        self._autofit = autofit
        self.dataframe = dataframe
        self.row_height = row_height
        self.column_width = column_width
        self.selected_cell = None
        self.selected_indices = set()
        self.render_queue = queue.Queue()

        # If a DataFrame is provided, extract columns and data
        if dataframe is not None:
            pass  # pandas is not accessed here
            self._columns = [""] + list(dataframe.columns)
            self._data = dataframe.reset_index().values.tolist()
        else:
            # Add a default header column with values 1, 2, 3, ...
            self._columns = [""] + self._columns
            self._data = [[i + 1] + row for i, row in enumerate(self._data)]

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create a canvas for the table
        self.canvas = tk.Canvas(self, bg=self.theme.background, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        # Add a vertical scrollbar
        self.scrollbar_v = CustomScrollbar(self, command=self.canvas.yview, theme=self.theme)
        self.scrollbar_v.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=self.scrollbar_v.set)
        
        # Add a horizontal scrollbar
        self.scrollvar_h = CustomScrollbar(self, orient="horizontal", command=self.canvas.xview, theme=self.theme)
        self.scrollvar_h.grid(row=1, column=0, sticky="ew")
        self.canvas.configure(xscrollcommand=self.scrollvar_h.set)

        # Create a frame inside the canvas for table content
        self.table_frame = tk.Frame(self.canvas, bg=self.theme.background)
        self.table_window = self.canvas.create_window((0, 0), window=self.table_frame, anchor="nw")

        # Bind scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Start rendering in a separate thread
        self._start_rendering()

    def _start_rendering(self):
        """Start rendering the table in a separate thread."""
        thread =  threading.Thread(target=self._render_table, daemon=True)
        thread.start()
        thread.join()
        threading.Thread(target=self._process_render_queue, daemon=True).start()
        
        # self.after_idle(self.after(50, self._process_render_queue))

    def _render_table(self):
        """Render the table headers and rows in a separate thread."""
        # Add column headers
        for col_index, col_name in enumerate(self._columns):
            self.render_queue.put(("header", col_index, col_name))

        # Add rows
        for row_index, row_data in enumerate(self._data):
            self.render_queue.put(("row", row_index, row_data))

    def _process_render_queue(self):
        """Process the render queue and update the UI."""
        try:
            while not self.render_queue.empty():
                item_type, index, data = self.render_queue.get_nowait()
                if item_type == "header":
                    self.after(0, self._draw_header, index, data)
                elif item_type == "row":
                    self.after(0, self._draw_row, index, data)
        except queue.Empty:
            pass
        finally:
            self.after(100, self.canvas.configure(scrollregion=self.canvas.bbox("all")))

    def _draw_header(self, col_index, col_name):
        """Draw a single column header."""
        header_bg = self.theme.border
        column_header_width = max([len(str(x[0])) for x in self._data]) + 2 if col_index == 0 else \
            max([len(str(x[col_index])) for x in self._data]) + 2 if self._autofit else self.column_width // 10
        header = tk.Label(self.table_frame, text=col_name, bg=header_bg,
                          fg=self.theme.text, font=self.theme.font, anchor="w",
                          width=column_header_width, height=1, padx=5, pady=5)
        header.grid(row=0, column=col_index, sticky="nsew", padx=1, pady=1)

        # Bind click event for column selection
        header.bind("<Button-1>", lambda _, c=col_index: self._select_column(c))

    def _draw_row(self, row_index, row_data):
        """Draw a single row."""
        # Add row headers
        row_header_bg = self.theme.border
        row_header = tk.Label(self.table_frame, text=row_data[0], bg=row_header_bg,
                              fg=self.theme.text, font=self.theme.font, anchor="w",
                              height=1, padx=5, pady=5)
        row_header.grid(row=row_index + 1, column=0, sticky="nsew", padx=1, pady=1)

        # Bind click event for row selection
        row_header.bind("<Button-1>", lambda _, r=row_index: self._select_row(r))

        # Add row cells
        for col_index, cell_data in enumerate(row_data):
            if col_index == 0:
                continue  # Skip the header column
            cell_bg = self.theme.widget_bg
            cell = tk.Label(self.table_frame, text=cell_data, bg=cell_bg,
                            fg=self.theme.text, font=self.theme.font, anchor="w",
                            width=self.column_width // 10, height=1, padx=5, pady=5)
            cell.grid(row=row_index + 1, column=col_index, sticky="nsew", padx=1, pady=1)

            # Bind hover and click events
            cell.bind("<Enter>", lambda e, r=row_index, c=col_index: self._on_cell_hover(e, r, c))
            cell.bind("<Leave>", lambda e, r=row_index, c=col_index: self._on_cell_leave(e, r, c))
            cell.bind("<Button-1>", lambda e, r=row_index, c=col_index: self._on_cell_click(e, r, c))

    def _on_mousewheel(self, event):
        """Scroll the canvas on mouse wheel."""
        if event.state & 0x0001 or event.state & 0x0004:  # Check if Shift or Alt key is pressed
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
        # Toggle selection of the clicked cell
        if (row, col) in self.selected_indices and col > 0:
            # Deselect the cell
            self.selected_indices.remove((row, col))
            event.widget.config(bg=self.theme.widget_bg)
        elif col > 0:
            # Select the cell
            self.selected_indices.add((row, col))
            event.widget.config(bg=self.theme.focus)

    def _select_row(self, row):
        """Toggle selection of an entire row."""
        row_indices = {(row, col) for col in range(len(self._columns)) if col != 0}
        if row_indices.issubset(self.selected_indices):
            # Deselect the entire row
            self.selected_indices -= row_indices
            for col in range(len(self._columns)):
                if col == 0: continue  # Skip the header column
                widget = self.table_frame.grid_slaves(row=row + 1, column=col)[0]
                widget.config(bg=self.theme.widget_bg)
        else:
            # Select the entire row
            self.selected_indices |= row_indices
            for col in range(len(self._columns)):
                if col == 0: continue  # Skip the header column
                widget = self.table_frame.grid_slaves(row=row + 1, column=col)[0]
                widget.config(bg=self.theme.focus)

    def _select_column(self, col):
        """Toggle selection of an entire column."""
        col_indices = {(row, col) for row in range(len(self._data))}
        
        if col_indices.issubset(self.selected_indices):
            if col == 0:
                # Deselect all rows and columns
                col_indices = {(row, c) for row in range(len(self._data)) for c in range(len(self._columns))}
                self.selected_indices -= col_indices
                for row in range(len(self._data)):
                    for c in range(len(self._columns)):
                        widget = self.table_frame.grid_slaves(row=row + 1, column=min(c+1,len(self._columns)-1))[0]
                        widget.config(bg=self.theme.widget_bg)
            else:
                # Deselect the entire column
                self.selected_indices -= col_indices
                for row in range(len(self._data)):
                    widget = self.table_frame.grid_slaves(row=row + 1, column=col)[0]
                    widget.config(bg=self.theme.widget_bg)
        else:
            if col == 0:
                # select all rows and columns
                col_indices = {(row, c) for row in range(len(self._data)) for c in range(len(self._columns))}
                self.selected_indices |= col_indices
                for row in range(len(self._data)):
                    for c in range(len(self._columns)):
                        widget = self.table_frame.grid_slaves(row=row + 1, column=min(c+1,len(self._columns)-1))[0]
                        widget.config(bg=self.theme.focus)
            else:
                # Select the entire column
                self.selected_indices |= col_indices
                for row in range(len(self._data)):
                    widget = self.table_frame.grid_slaves(row=row + 1, column=col)[0]
                    widget.config(bg=self.theme.focus)

    def get_selected_indices(self):
        """Return the indices of selected cells."""
        selected_indices = {(row, col-1) for row, col in self.selected_indices if col > 0}
        return selected_indices

    def set_data(self, data):
        """Update the table data and redraw."""
        self._data = [[i + 1] + row for i, row in enumerate(data)]
        self._draw_table()
        
    def set_columns(self, columns):
        """Set new column names and redraw the table."""
        self._columns = [""] + columns
        self._draw_table()
        
    def set_dataframe_from_csv(self, csv_file):
        """Set a pandas DataFrame from a CSV file as the table data."""
        import pandas as pd
        dataframe = pd.read_csv(csv_file)
        self.set_dataframe(dataframe)
        
    def get_column_headers(self):
        """Return the current column names."""
        return self._columns[1:]

    def get_data(self):
        """Return the current table data."""
        return [row[1:] for row in self._data]
    
    def get_row_headers(self):
        """Return the current row names."""
        return [row[0] for row in self._data]
    
    def set_dataframe(self, dataframe):
        """Set a pandas DataFrame as the table data."""
        self._columns = [""] + list(dataframe.columns)
        self._data = dataframe.reset_index().values.tolist()
        self._draw_table()

    def add_row(self, row_data):
        """Add a new row to the table."""
        self._data.append([len(self._data) + 1] + row_data)
        self._draw_table()

    def clear_data(self):
        """Clear all table data."""
        self._data = []
        self._draw_table()

if __name__ == "__main__":
    from Tk import Tk
    import pandas as pd

    root = Tk(theme_mode="dark")
    root.title("Custom TableView Demo")
    root.geometry("600x400")

    columns = [f'col {i}' for i in range(4)]
    index  = [f'row {i}' for i in range(1000)]
    data = [[f'cell {c}' for c in columns] for i in index]
    dataframe = pd.DataFrame(data, columns=columns, index=index)

    table = CustomTableView(root, columns=columns, dataframe=dataframe, column_width=150, theme=root.theme)
    table.pack(fill="both", expand=True, padx=10, pady=10)

    def show_selected():
        print("Selected Indices:", table.get_selected_indices())

    from Button import CustomButton
    show_button = CustomButton(root, text="Show Selected", command=show_selected)
    show_button.pack(pady=10)

    root.mainloop()