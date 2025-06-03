import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
from collections import defaultdict
from datetime import datetime
import matplotlib.pyplot as plt

class FinancialNotebook(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Financial Notebook")
        self.geometry("800x400")
        self.create_widgets()
        self.data = []

    def create_widgets(self):
        self.toolbar = tk.Frame(self)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        tk.Button(self.toolbar, text="New", command=self.new_sheet).pack(side=tk.LEFT)
        tk.Button(self.toolbar, text="Open", command=self.open_file).pack(side=tk.LEFT)
        tk.Button(self.toolbar, text="Save", command=self.save_file).pack(side=tk.LEFT)
        tk.Button(self.toolbar, text="Add Row", command=self.add_row).pack(side=tk.LEFT)
        tk.Button(self.toolbar, text="Delete Row", command=self.delete_row).pack(side=tk.LEFT)
        tk.Button(self.toolbar, text="Show Graphs", command=self.show_graphs).pack(side=tk.LEFT)

        columns = ["Date", "Description", "Category", "Amount"]
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind('<Double-1>', self.edit_cell)

    def new_sheet(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.data = []

    def open_file(self):
        file = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file:
            self.new_sheet()
            with open(file, newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    self.tree.insert("", tk.END, values=row)
                    self.data.append(row)

    def save_file(self):
        file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if file:
            with open(file, "w", newline='') as f:
                writer = csv.writer(f)
                for row_id in self.tree.get_children():
                    row = self.tree.item(row_id)['values']
                    writer.writerow(row)
            messagebox.showinfo("Saved", "File saved successfully.")

    def add_row(self):
        self.tree.insert("", tk.END, values=["", "", "", ""])

    def delete_row(self):
        selected = self.tree.selection()
        for item in selected:
            self.tree.delete(item)

    def edit_cell(self, event):
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        if not item or not column:
            return
        col = int(column.replace('#', '')) - 1
        x, y, width, height = self.tree.bbox(item, column)
        value = self.tree.item(item, 'values')[col]
        entry = tk.Entry(self.tree)
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, value)
        entry.focus()

        def save_edit(event):
            new_value = entry.get()
            values = list(self.tree.item(item, 'values'))
            values[col] = new_value
            self.tree.item(item, values=values)
            entry.destroy()

        entry.bind('<Return>', save_edit)
        entry.bind('<FocusOut>', lambda e: entry.destroy())

    def show_graphs(self):
        category_data = defaultdict(float)
        date_data = defaultdict(float)

        for row_id in self.tree.get_children():
            row = self.tree.item(row_id)['values']
            if len(row) >= 4:
                category = row[2].strip()
                try:
                    amount = float(row[3])
                    date_str = row[0].strip()
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")  # strict format
                    category_data[category] += amount
                    date_data[date_obj.date()] += amount
                except Exception:
                    continue  # skip invalid data

        if not category_data and not date_data:
            messagebox.showinfo("No Data", "No valid data to plot.")
            return

        # Plot Pie Chart
        plt.figure(figsize=(12, 5))

        plt.subplot(1, 2, 1)
        plt.pie(category_data.values(), labels=category_data.keys(), autopct='%1.1f%%', startangle=140)
        plt.title("Expenses by Category")
        plt.axis('equal')

        # Plot Line Chart
        plt.subplot(1, 2, 2)
        sorted_dates = sorted(date_data.items())
        dates = [d[0] for d in sorted_dates]
        amounts = [d[1] for d in sorted_dates]
        plt.plot(dates, amounts, marker='o', linestyle='-', color='blue')
        plt.title("Expenses Over Time")
        plt.xlabel("Date")
        plt.ylabel("Amount")
        plt.xticks(rotation=45)
        plt.tight_layout()

        plt.show()

if __name__ == "__main__":
    app = FinancialNotebook()
    app.mainloop()
