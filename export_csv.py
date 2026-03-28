"""
FILE: export_csv.py
PURPOSE: Export transactions to CSV
"""

import csv
from datetime import datetime
from tkinter import filedialog, messagebox

def export_all_transactions_to_csv(transactions):
    try:
        if not transactions:
            messagebox.showwarning("No Data", "No transactions to export!")
            return False
        
        current_date = datetime.now().strftime("%d-%m-%Y")
        default_filename = f"wlist_transactions_{current_date}.csv"
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=default_filename,
            title="Save Transactions as CSV"
        )
        
        if not file_path:
            return False
        
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Date', 'Time', 'Item Name', 'Amount', 'Currency', 'Note']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for trans in transactions:
                writer.writerow({
                    'Date': trans.get('transaction_date', ''),
                    'Time': trans.get('transaction_time', ''),
                    'Item Name': trans.get('item_name', ''),
                    'Amount': trans.get('amount', 0),
                    'Currency': trans.get('currency', 'Rs'),
                    'Note': trans.get('note', '')
                })
        
        messagebox.showinfo("Success", f"Exported {len(transactions)} transactions!")
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Failed: {str(e)}")
        return False

def export_item_transactions_to_csv(item_name, transactions):
    try:
        if not transactions:
            messagebox.showwarning("No Data", "No transactions!")
            return False
        
        current_date = datetime.now().strftime("%d-%m-%Y")
        safe_name = "".join(c for c in item_name if c.isalnum() or c in ' ')
        default_filename = f"wlist_{safe_name}_{current_date}.csv"
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=default_filename,
            title="Save Transactions as CSV"
        )
        
        if not file_path:
            return False
        
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Date', 'Time', 'Amount', 'Currency', 'Note']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for trans in transactions:
                writer.writerow({
                    'Date': trans.get('transaction_date', ''),
                    'Time': trans.get('transaction_time', ''),
                    'Amount': trans.get('amount', 0),
                    'Currency': trans.get('currency', 'Rs'),
                    'Note': trans.get('note', '')
                })
        
        messagebox.showinfo("Success", f"Exported {len(transactions)} transactions!")
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Failed: {str(e)}")
        return False
