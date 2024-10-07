import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox

def read_reference_csv(file_path):
    df = pd.read_csv(file_path)
    df.columns = [col.strip().upper() for col in df.columns]  # Convert columns to uppercase
    pipelines = {}
    for pipeline, group in df.groupby('PIPELINE'):
        first_row = group.iloc[0]
        last_row = group.iloc[-1]
        pipelines[pipeline] = {
            'start': first_row,
            'end': last_row
        }
    return pipelines

def read_text_files(file_paths):
    data = {}
    for file_path in file_paths:
        df = pd.read_csv(file_path)
        df.columns = [col.strip().upper() for col in df.columns]  # Convert columns to uppercase
        first_row = df.iloc[0]
        last_row = df.iloc[-1]
        ID = first_row['ID']  # Ensure 'ID' is in uppercase
        data[ID] = {
            'start': first_row,
            'end': last_row,
            'file_path': file_path
        }
    return data

def compare_rows_custom(row1, row2, columns1, columns2, tolerance=0.001):
    discrepancies = []
    for col1, col2 in zip(columns1, columns2):
        try:
            val1 = float(row1[col1])
            val2 = float(row2[col2])
            if abs(val1 - val2) > tolerance:
                discrepancies.append(f"  Column '{col1}' vs '{col2}': File value = {val1}, Reference value = {val2}")
        except ValueError:
            val1 = str(row1[col1]).strip()
            val2 = str(row2[col2]).strip()
            if val1 != val2:
                discrepancies.append(f"  Column '{col1}' vs '{col2}': File value = {val1}, Reference value = {val2}")
        except KeyError as e:
            discrepancies.append(f"  Missing column: {e}")
    return discrepancies

def cross_check(data_from_files, reference_data):
    report = ""
    columns_to_compare_file = ['EASTING', 'NORTHING', 'KP']
    columns_to_compare_reference = ['EASTING', 'NORTHING', 'KP_NEW']
    for ID, file_data in data_from_files.items():
        if ID in reference_data:
            ref_data = reference_data[ID]
            discrepancies = []
            # Compare start points
            start_discrepancies = compare_rows_custom(
                file_data['start'],
                ref_data['start'],
                columns_to_compare_file,
                columns_to_compare_reference
            )
            if start_discrepancies:
                discrepancies.append(f"Start point discrepancies for {ID}:\n" + "\n".join(start_discrepancies))
            # Compare end points
            end_discrepancies = compare_rows_custom(
                file_data['end'],
                ref_data['end'],
                columns_to_compare_file,
                columns_to_compare_reference
            )
            if end_discrepancies:
                discrepancies.append(f"End point discrepancies for {ID}:\n" + "\n".join(end_discrepancies))
            if discrepancies:
                report += f"Discrepancies for {ID}:\n" + "\n".join(discrepancies) + "\n\n"
            else:
                report += f"No discrepancies found for {ID}.\n\n"
        else:
            report += f"ID '{ID}' from file '{file_data['file_path']}' not found in reference data.\n\n"
    return report

def select_reference_file():
    file_path = filedialog.askopenfilename(
        title="Select Reference CSV File",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )
    reference_entry.delete(0, tk.END)
    reference_entry.insert(0, file_path)

def select_text_files():
    files = filedialog.askopenfilenames(
        title="Select Text Files",
        filetypes=[
            ("QPS files", "*.qps"),
            ("Text files", "*.txt"),
            ("CSV files", "*.csv"),
            ("All files", "*.*")
        ]
    )
    files_entry.delete(0, tk.END)
    files_entry.insert(0, ', '.join(files))

def run_cross_check():
    try:
        # Get user inputs
        reference_file = reference_entry.get()
        text_files = files_entry.get().split(', ')
        
        # Read files
        reference_data = read_reference_csv(reference_file)
        data_from_files = read_text_files(text_files)
        
        # Perform cross-check
        report = cross_check(data_from_files, reference_data)
        
        # Display report
        report_window = tk.Toplevel(root)
        report_window.title("Cross-Check Report")
        text_widget = tk.Text(report_window, wrap='word')
        text_widget.insert('1.0', report)
        text_widget.pack()
    except Exception as e:
        messagebox.showerror("Error", str(e))

root = tk.Tk()
root.title("Cross-Check Tool")

# Reference file selection
tk.Label(root, text="Reference CSV File:").grid(row=0, column=0, sticky=tk.W)
reference_entry = tk.Entry(root, width=50)
reference_entry.grid(row=0, column=1)
tk.Button(root, text="Browse...", command=select_reference_file).grid(row=0, column=2)

# Text files selection
tk.Label(root, text="Text Files:").grid(row=1, column=0, sticky=tk.W)
files_entry = tk.Entry(root, width=50)
files_entry.grid(row=1, column=1)
tk.Button(root, text="Browse...", command=select_text_files).grid(row=1, column=2)

# Run button
tk.Button(root, text="Run Cross-Check", command=run_cross_check).grid(row=2, column=1)

root.mainloop()
