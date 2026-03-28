import tkinter as tk
from tkinter import ttk, messagebox
from database import (
    get_all_wishlist_items, get_wishlist_item_by_id, create_wishlist_item,
    delete_wishlist_item, update_wishlist_item_name, add_transaction,
    get_transactions_by_item_id, get_all_transactions, get_total_savings,
    calculate_progress_percentage, get_progress_color, can_add_amount
)
from export_csv import export_all_transactions_to_csv, export_item_transactions_to_csv
from constants import COLORS, FONTS, APP_TITLE, APP_WIDTH, APP_HEIGHT

class WListApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.root.configure(bg=COLORS["bg_main"])
        
        self.is_fullscreen = False
        
        self.create_ui()
        self.refresh_data()
    
    def create_ui(self):
        self.main_frame = tk.Frame(self.root, bg=COLORS["bg_main"])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_frame = tk.Frame(self.main_frame, bg=COLORS["bg_main"])
        title_frame.pack(pady=(0, 10))
        
        tk.Label(title_frame, text="W - L I S T", font=FONTS["title"],
                bg=COLORS["bg_main"], fg=COLORS["primary"]).pack()
        
        tk.Label(title_frame, text="=" * 50, font=FONTS["normal"],
                bg=COLORS["bg_main"], fg=COLORS["primary"]).pack()
        
        # Total Savings Card
        self.total_frame = tk.Frame(self.main_frame, bg=COLORS["primary"], padx=20, pady=15, relief=tk.RAISED, bd=2)
        self.total_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.total_label = tk.Label(self.total_frame, text="TOTAL SAVINGS: Rs 0",
                                   font=FONTS["heading"], bg=COLORS["primary"], fg=COLORS["text_primary"])
        self.total_label.pack()
        
        # Action Buttons
        btn_frame = tk.Frame(self.main_frame, bg=COLORS["bg_main"])
        btn_frame.pack(pady=(0, 10))
        
        tk.Button(btn_frame, text="[ DOWNLOAD CSV ]", font=FONTS["button"],
                 bg=COLORS["primary"], fg=COLORS["text_primary"], relief=tk.FLAT, bd=0,
                 padx=15, pady=8, cursor="hand2", command=self.download_csv).pack(side=tk.LEFT, padx=4)
        
        tk.Button(btn_frame, text="[ VIEW ALL TRANSACTIONS ]", font=FONTS["button"],
                 bg=COLORS["secondary"], fg=COLORS["text_primary"], relief=tk.FLAT, bd=0,
                 padx=15, pady=8, cursor="hand2", command=self.show_all_transactions_popup).pack(side=tk.LEFT, 
padx=4)
        
        tk.Button(btn_frame, text="[ FULLSCREEN ]", font=FONTS["button"],
                 bg=COLORS["danger"], fg=COLORS["text_primary"], relief=tk.FLAT, bd=0,
                 padx=15, pady=8, cursor="hand2", command=self.toggle_fullscreen).pack(side=tk.LEFT, padx=4)
        
        # Wishlists Header
        header_frame = tk.Frame(self.main_frame, bg=COLORS["bg_main"])
        header_frame.pack(fill=tk.X, pady=(10, 5))
        
        tk.Label(header_frame, text="> MY WISHLISTS", font=FONTS["subheading"],
                bg=COLORS["bg_main"], fg=COLORS["primary"]).pack(side=tk.LEFT)
        
        tk.Label(header_frame, text="=" * 50, font=FONTS["normal"],
                bg=COLORS["bg_main"], fg=COLORS["primary"]).pack(side=tk.LEFT, padx=10)
        
        # Wishlist Container with Scrollbar
        self.wishlist_container = tk.Frame(self.main_frame, bg=COLORS["bg_main"])
        self.wishlist_container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas for scrolling
        self.canvas = tk.Canvas(self.wishlist_container, bg=COLORS["bg_main"], highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Custom thin scrollbar - Ubuntu terminal style
        style = ttk.Style()
        style.theme_use("default")
        
        # Configure thin red scrollbar
        style.configure(
            "Custom.Vertical.TScrollbar",
            gripcount=0,
            background=COLORS["primary"],      # Red thumb
            troughcolor=COLORS["bg_card"],      # Dark trough
            arrowcolor=COLORS["primary"],       # Red arrows
            thickness=10,                       # Thin (10px like Ubuntu)
            arrowsize=12
        )
        
        # Create scrollbar with custom style
        self.scrollbar = ttk.Scrollbar(
            self.wishlist_container,
            orient=tk.VERTICAL,
            command=self.canvas.yview,
            style="Custom.Vertical.TScrollbar"
        )
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Inner frame for wishlist cards
        self.inner_frame = tk.Frame(self.canvas, bg=COLORS["bg_main"])
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor=tk.NW)
        
        # Bind configure to update scroll region
        self.inner_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        # Mousewheel scrolling
        def on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Add Button
        tk.Button(self.main_frame, text="[ + ADD NEW WISHLIST ]", font=("Courier New", 12, "bold"),
                 bg=COLORS["success"], fg=COLORS["text_dark"], relief=tk.FLAT, bd=0,
                 padx=30, pady=12, cursor="hand2", command=self.show_add_popup).pack(fill=tk.X, pady=10)
        
        # Keyboard shortcuts
        self.root.bind('<Control-Escape>', lambda e: self.toggle_fullscreen())
        self.root.bind('<Escape>', lambda e: self.exit_fullscreen())
    
    def refresh_data(self):
        try:
            total = get_total_savings()
            self.total_label.config(text=f"TOTAL SAVINGS: Rs {total:,.2f}")
            
            # Clear inner frame widgets
            for widget in self.inner_frame.winfo_children():
                widget.destroy()
            
            items = get_all_wishlist_items()
            
            if not items:
                tk.Label(self.inner_frame, text="No wishlists yet. Click [ + ADD NEW WISHLIST ] to start!",
                        font=FONTS["normal"], bg=COLORS["bg_main"],
                        fg=COLORS["text_secondary"]).pack(pady=20)
            else:
                for item in items:
                    self.create_wishlist_card(item)
            
            # Update scroll region after adding widgets
            self.inner_frame.update_idletasks()
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def create_wishlist_card(self, item):
        card = tk.Frame(self.inner_frame, bg=COLORS["bg_card"], relief=tk.RAISED, bd=1,
                       highlightbackground=COLORS["primary"], highlightthickness=1)
        card.pack(fill=tk.X, pady=8, padx=2)
        
        percentage = calculate_progress_percentage(item['total_saved'], item['target_price'])
        progress_color = get_progress_color(percentage)
        remaining = item['target_price'] - item['total_saved']
        
        # Header
        header = tk.Frame(card, bg=COLORS["bg_card"])
        header.pack(fill=tk.X, padx=15, pady=(15, 5))
        
        icon_map = {
            "P": "[PHONE]", "L": "[LAPTOP]", "C": "[CAR]", "H": "[HOME]",
            "T": "[TRAVEL]", "G": "[GAME]", "Cam": "[CAMERA]", "W": "[WATCH]",
            "B": "[BIKE]", "Bi": "[BAG]", "Gi": "[GIFT]", "S": "[SPORTS]"
        }
        icon_text = icon_map.get(item['icon'], "[*]")
        
        tk.Label(header, text=icon_text, font=("Courier New", 16),
                bg=COLORS["bg_card"], fg=COLORS["primary"]).pack(side=tk.LEFT)
        
        tk.Label(header, text=item['item_name'], font=FONTS["subheading"],
                bg=COLORS["bg_card"], fg=COLORS["text_primary"]).pack(side=tk.LEFT, padx=10)
        
        # Progress Bar
        progress_frame = tk.Frame(card, bg=COLORS["bg_card"])
        progress_frame.pack(fill=tk.X, padx=15, pady=5)
        
        canvas = tk.Canvas(progress_frame, height=14, bg=COLORS["bg_card"], highlightthickness=0)
        canvas.pack(fill=tk.X)
        
        canvas.create_rectangle(0, 0, 600, 14, fill="#220000", outline="")
        
        width = (percentage / 100) * 600
        canvas.create_rectangle(0, 0, width, 14, fill=progress_color, outline="")
        
        percent_text = f"{percentage:.1f}%"
        if percentage >= 100:
            percent_text = "100% COMPLETED"
        
        tk.Label(progress_frame, text=percent_text, font=FONTS["percentage"],
                bg=COLORS["bg_card"], fg=progress_color).pack(anchor=tk.E)
        
        # Details
        details = tk.Frame(card, bg=COLORS["bg_card"])
        details.pack(fill=tk.X, padx=15, pady=5)
        
        curr = item['currency']
        tk.Label(details, text=f"Target: {curr} {item['target_price']:,.0f}", font=FONTS["normal"],
                bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).pack(side=tk.LEFT, padx=8)
        tk.Label(details, text=f"Saved: {curr} {item['total_saved']:,.0f}", font=FONTS["money"],
                bg=COLORS["bg_card"], fg=COLORS["success"]).pack(side=tk.LEFT, padx=8)
        tk.Label(details, text=f"Left: {curr} {remaining:,.0f}", font=FONTS["normal"],
                bg=COLORS["bg_card"], fg=COLORS["danger"]).pack(side=tk.LEFT, padx=8)
        
        # Buttons
        buttons = tk.Frame(card, bg=COLORS["bg_card"], pady=12)
        buttons.pack(fill=tk.X, padx=15)
        
        btn_style = {"relief": tk.FLAT, "bd": 0, "font": FONTS["button"], "cursor": "hand2", "padx": 10, "pady": 5}
        
        tk.Button(buttons, text="[ ADD MONEY ]", bg=COLORS["success"], fg=COLORS["text_dark"],
                 **btn_style, command=lambda: self.show_add_money_popup(item['id'])).pack(side=tk.LEFT, padx=3)
        tk.Button(buttons, text="[ RENAME ]", bg=COLORS["warning"], fg=COLORS["text_dark"],
                 **btn_style, command=lambda: self.show_rename_popup(item['id'])).pack(side=tk.LEFT, padx=3)
        tk.Button(buttons, text="[ DELETE ]", bg=COLORS["danger"], fg=COLORS["text_primary"],
                 **btn_style, command=lambda: self.show_delete_popup(item['id'])).pack(side=tk.LEFT, padx=3)
        tk.Button(buttons, text="[ HISTORY ]", bg=COLORS["info"], fg=COLORS["text_primary"],
                 **btn_style, command=lambda: self.show_item_history_popup(item['id'])).pack(side=tk.LEFT, padx=3)
    
    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes('-fullscreen', self.is_fullscreen)
    
    def exit_fullscreen(self):
        if self.is_fullscreen:
            self.toggle_fullscreen()
    
    # ============ POPUP METHODS ============
    
    def show_add_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("ADD WISHLIST")
        popup.geometry("450x550")
        popup.configure(bg=COLORS["bg_main"])
        popup.transient(self.root)
        popup.grab_set()
        
        tk.Label(popup, text="ADD NEW WISHLIST", font=FONTS["heading"],
                bg=COLORS["bg_main"], fg=COLORS["primary"]).pack(pady=20)
        
        # Icon Selection
        tk.Label(popup, text="Select Icon:", font=FONTS["normal"],
                bg=COLORS["bg_main"], fg=COLORS["text_primary"]).pack(anchor=tk.W, padx=40, pady=(10, 0))
        
        icon_frame = tk.Frame(popup, bg=COLORS["bg_main"])
        icon_frame.pack(pady=5)
        
        icons = ["P", "L", "C", "H", "T", "G", "Cam", "W", "B", "Bi", "Gi", "S"]
        icon_labels = {"P": "[P]", "L": "[L]", "C": "[C]", "H": "[H]", "T": "[T]", "G": "[G]",
                      "Cam": "[Cam]", "W": "[W]", "B": "[B]", "Bi": "[Bi]", "Gi": "[Gi]", "S": "[S]"}
        icon_var = tk.StringVar(value="P")
        
        for i, ic in enumerate(icons):
            tk.Radiobutton(icon_frame, text=icon_labels[ic], variable=icon_var, value=ic,
                          font=FONTS["normal"], bg=COLORS["bg_main"], fg=COLORS["text_primary"],
                          selectcolor=COLORS["primary"]).grid(row=i//4, column=i%4, padx=5, pady=2)
        
        # Category
        tk.Label(popup, text="Category:", font=FONTS["normal"],
                bg=COLORS["bg_main"], fg=COLORS["text_primary"]).pack(anchor=tk.W, padx=40, pady=(10, 0))
        
        categories = ["Phone", "Laptop", "Car", "Bike", "Home", "Travel", "Camera", "Watch", "Bag", "Plane", "Game", 
"Gift"]
        cat_var = tk.StringVar(value="Phone")
        ttk.Combobox(popup, textvariable=cat_var, values=categories, font=FONTS["normal"], width=25).pack(pady=5)
        
        # Item Name
        tk.Label(popup, text="Item Name:", font=FONTS["normal"],
                bg=COLORS["bg_main"], fg=COLORS["text_primary"]).pack(anchor=tk.W, padx=40, pady=(10, 0))
        name_entry = tk.Entry(popup, font=FONTS["normal"], width=35, bg=COLORS["bg_card"], relief=tk.FLAT, bd=2)
        name_entry.pack(pady=5)
        
        # Target Price
        tk.Label(popup, text="Target Price:", font=FONTS["normal"],
                bg=COLORS["bg_main"], fg=COLORS["text_primary"]).pack(anchor=tk.W, padx=40, pady=(10, 0))
        price_entry = tk.Entry(popup, font=FONTS["normal"], width=35, bg=COLORS["bg_card"], relief=tk.FLAT, bd=2)
        price_entry.pack(pady=5)
        
        # Currency
        tk.Label(popup, text="Select Currency:", font=FONTS["normal"],
                bg=COLORS["bg_main"], fg=COLORS["text_primary"]).pack(anchor=tk.W, padx=40, pady=(10, 0))
        
        curr_frame = tk.Frame(popup, bg=COLORS["bg_main"])
        curr_frame.pack(pady=5)
        
        currencies = [("Rs", "INR"), ("$", "USD"), ("Euro", "EUR"), ("Pound", "GBP"), ("Yen", "JPY"), ("Won", 
"KRW")]
        curr_var = tk.StringVar(value="Rs")
        
        for i, (sym, code) in enumerate(currencies):
            tk.Radiobutton(curr_frame, text=f"{sym} {code}", variable=curr_var, value=sym,
                          font=FONTS["small"], bg=COLORS["bg_main"], fg=COLORS["text_primary"],
                          selectcolor=COLORS["primary"]).grid(row=i//3, column=i%3, padx=8, pady=2)
        
        # Buttons
        btn_frame = tk.Frame(popup, bg=COLORS["bg_main"])
        btn_frame.pack(pady=20)
        
        def save():
            try:
                icon = icon_var.get()
                name = name_entry.get().strip()
                currency = curr_var.get()
                
                if not name:
                    messagebox.showerror("Error", "Please enter item name!")
                    return
                
                try:
                    target = float(price_entry.get())
                    if target <= 0:
                        messagebox.showerror("Error", "Target must be greater than 0!")
                        return
                except:
                    messagebox.showerror("Error", "Invalid target price!")
                    return
                
                create_wishlist_item(icon, name, currency, target)
                popup.destroy()
                self.refresh_data()
                messagebox.showinfo("Success", f"Added: {name}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        tk.Button(btn_frame, text="[ CANCEL ]", font=FONTS["button"], bg=COLORS["danger"],
                 fg=COLORS["text_primary"], relief=tk.FLAT, bd=0, padx=20, pady=8,
                 command=popup.destroy).pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="[ CREATE ]", font=FONTS["button"], bg=COLORS["success"],
                 fg=COLORS["text_dark"], relief=tk.FLAT, bd=0, padx=20, pady=8,
                 command=save).pack(side=tk.LEFT, padx=10)
    
    def show_add_money_popup(self, item_id):
        item = get_wishlist_item_by_id(item_id)
        if not item:
            messagebox.showerror("Error", "Item not found!")
            return
        
        remaining = item['target_price'] - item['total_saved']
        
        popup = tk.Toplevel(self.root)
        popup.title("ADD MONEY")
        popup.geometry("400x380")
        popup.configure(bg=COLORS["bg_main"])
        popup.transient(self.root)
        popup.grab_set()
        
        curr = item['currency']
        
        tk.Label(popup, text="ADD MONEY", font=FONTS["heading"],
                bg=COLORS["bg_main"], fg=COLORS["primary"]).pack(pady=20)
        
        tk.Label(popup, text=f"Item: {item['item_name']}", font=FONTS["normal"],
                bg=COLORS["bg_main"], fg=COLORS["text_primary"]).pack()
        
        # Info
        info_frame = tk.Frame(popup, bg=COLORS["bg_card"], padx=20, pady=15)
        info_frame.pack(pady=10)
        
        tk.Label(info_frame, text=f"Target: {curr} {item['target_price']:,.0f}", font=FONTS["normal"],
                bg=COLORS["bg_card"], fg=COLORS["text_secondary"]).pack()
        tk.Label(info_frame, text=f"Already Saved: {curr} {item['total_saved']:,.0f}", font=FONTS["money"],
                bg=COLORS["bg_card"], fg=COLORS["success"]).pack()
        tk.Label(info_frame, text=f"Remaining: {curr} {remaining:,.0f}", font=FONTS["normal"],
                bg=COLORS["bg_card"], fg=COLORS["danger"]).pack()
        
        # Amount
        tk.Label(popup, text=f"Amount to Add ({curr}):", font=FONTS["normal"],
                bg=COLORS["bg_main"], fg=COLORS["text_primary"]).pack(anchor=tk.W, padx=40, pady=(10, 0))
        
        amount_entry = tk.Entry(popup, font=FONTS["normal"], width=25, bg=COLORS["bg_card"], relief=tk.FLAT, bd=2)
        amount_entry.pack(pady=5)
        
        tk.Label(popup, text=f"Maximum you can add: {curr} {remaining:,.0f}", font=FONTS["small"],
                bg=COLORS["bg_main"], fg=COLORS["warning"]).pack()
        
        # Note
        tk.Label(popup, text="Note (Optional):", font=FONTS["normal"],
                bg=COLORS["bg_main"], fg=COLORS["text_primary"]).pack(anchor=tk.W, padx=40, pady=(10, 0))
        note_entry = tk.Entry(popup, font=FONTS["normal"], width=25, bg=COLORS["bg_card"], relief=tk.FLAT, bd=2)
        note_entry.pack(pady=5)
        
        # Buttons
        btn_frame = tk.Frame(popup, bg=COLORS["bg_main"])
        btn_frame.pack(pady=20)
        
        def save_money():
            try:
                amount_str = amount_entry.get().strip()
                note = note_entry.get().strip()
                
                if not amount_str:
                    messagebox.showerror("Error", "Please enter amount!")
                    return
                
                try:
                    amount = float(amount_str)
                    if amount <= 0:
                        messagebox.showerror("Error", "Amount must be greater than 0!")
                        return
                    
                    if amount > remaining:
                        messagebox.showerror("Error", f"Cannot add more than remaining amount ({curr} {remaining:,.0f})!")
                        return
                        
                except:
                    messagebox.showerror("Error", "Invalid amount!")
                    return
                
                add_transaction(item_id, amount, note, curr)
                popup.destroy()
                self.refresh_data()
                messagebox.showinfo("Success", f"Added {curr} {amount:,.0f}!")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        tk.Button(btn_frame, text="[ CANCEL ]", font=FONTS["button"], bg=COLORS["danger"],
                 fg=COLORS["text_primary"], relief=tk.FLAT, bd=0, padx=20, pady=8,
                 command=popup.destroy).pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="[ ADD MONEY ]", font=FONTS["button"], bg=COLORS["success"],
                 fg=COLORS["text_dark"], relief=tk.FLAT, bd=0, padx=20, pady=8,
                 command=save_money).pack(side=tk.LEFT, padx=10)
    
    def show_rename_popup(self, item_id):
        item = get_wishlist_item_by_id(item_id)
        if not item:
            messagebox.showerror("Error", "Item not found!")
            return
        
        popup = tk.Toplevel(self.root)
        popup.title("RENAME")
        popup.geometry("400x200")
        popup.configure(bg=COLORS["bg_main"])
        popup.transient(self.root)
        popup.grab_set()
        
        tk.Label(popup, text="RENAME ITEM", font=FONTS["heading"],
                bg=COLORS["bg_main"], fg=COLORS["primary"]).pack(pady=20)
        
        tk.Label(popup, text=f"Current: {item['item_name']}", font=FONTS["normal"],
                bg=COLORS["bg_main"], fg=COLORS["text_secondary"]).pack()
        
        tk.Label(popup, text="New Name:", font=FONTS["normal"],
                bg=COLORS["bg_main"], fg=COLORS["text_primary"]).pack(anchor=tk.W, padx=40, pady=(15, 0))
        
        name_entry = tk.Entry(popup, font=FONTS["normal"], width=35, bg=COLORS["bg_card"], relief=tk.FLAT, bd=2)
        name_entry.insert(0, item['item_name'])
        name_entry.pack(pady=5)
        
        btn_frame = tk.Frame(popup, bg=COLORS["bg_main"])
        btn_frame.pack(pady=20)
        
        def save_name():
            new_name = name_entry.get().strip()
            if not new_name:
                messagebox.showerror("Error", "Please enter name!")
                return
            
            update_wishlist_item_name(item_id, new_name)
            popup.destroy()
            self.refresh_data()
            messagebox.showinfo("Success", "Renamed!")
        
        tk.Button(btn_frame, text="[ CANCEL ]", font=FONTS["button"], bg=COLORS["danger"],
                 fg=COLORS["text_primary"], relief=tk.FLAT, bd=0, padx=20, pady=8,
                 command=popup.destroy).pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="[ SAVE ]", font=FONTS["button"], bg=COLORS["success"],
                 fg=COLORS["text_dark"], relief=tk.FLAT, bd=0, padx=20, pady=8,
                 command=save_name).pack(side=tk.LEFT, padx=10)
    
    def show_delete_popup(self, item_id):
        item = get_wishlist_item_by_id(item_id)
        if not item:
            messagebox.showerror("Error", "Item not found!")
            return
        
        popup = tk.Toplevel(self.root)
        popup.title("DELETE")
        popup.geometry("400x180")
        popup.configure(bg=COLORS["bg_main"])
        popup.transient(self.root)
        popup.grab_set()
        
        tk.Label(popup, text="WARNING!", font=("Courier New", 18, "bold"),
                bg=COLORS["bg_main"], fg=COLORS["danger"]).pack(pady=15)
        
        tk.Label(popup, text=f"Delete: {item['item_name']}?", font=FONTS["normal"],
                bg=COLORS["bg_main"], fg=COLORS["text_primary"]).pack()
        
        tk.Label(popup, text="All transaction history will be deleted!",
                font=FONTS["small"], bg=COLORS["bg_main"], fg=COLORS["danger"]).pack()
        
        btn_frame = tk.Frame(popup, bg=COLORS["bg_main"])
        btn_frame.pack(pady=20)
        
        def confirm():
            delete_wishlist_item(item_id)
            popup.destroy()
            self.refresh_data()
            messagebox.showinfo("Success", "Deleted!")
        
        tk.Button(btn_frame, text="[ CANCEL ]", font=FONTS["button"], bg=COLORS["success"],
                 fg=COLORS["text_dark"], relief=tk.FLAT, bd=0, padx=20, pady=8,
                 command=popup.destroy).pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="[ DELETE ]", font=FONTS["button"], bg=COLORS["danger"],
                 fg=COLORS["text_primary"], relief=tk.FLAT, bd=0, padx=20, pady=8,
                 command=confirm).pack(side=tk.LEFT, padx=10)
    
    def show_item_history_popup(self, item_id):
        item = get_wishlist_item_by_id(item_id)
        if not item:
            messagebox.showerror("Error", "Item not found!")
            return
        
        transactions = get_transactions_by_item_id(item_id)
        
        popup = tk.Toplevel(self.root)
        popup.title("HISTORY")
        popup.geometry("650x500")
        popup.configure(bg=COLORS["bg_main"])
        
        curr = item['currency']
        
        tk.Label(popup, text=f"HISTORY: {item['item_name']}", font=FONTS["heading"],
                bg=COLORS["primary"], fg=COLORS["text_primary"], padx=20, pady=10).pack(fill=tk.X)
        
        total = sum(t['amount'] for t in transactions)
        tk.Label(popup, text=f"Transactions: {len(transactions)} | Total: {curr} {total:,.0f}",
                font=FONTS["normal"], bg=COLORS["bg_card"], padx=20, pady=10).pack(fill=tk.X)
        
        # List
        list_frame = tk.Frame(popup, bg=COLORS["bg_main"])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        cols = ('date', 'time', 'amount', 'note')
        tree = ttk.Treeview(list_frame, columns=cols, show='headings')
        
        for col in cols:
            tree.heading(col, text=col.capitalize())
        
        tree.column('date', width=100)
        tree.column('time', width=80)
        tree.column('amount', width=120)
        tree.column('note', width=200)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        for trans in transactions:
            tree.insert('', tk.END, values=(
                trans['transaction_date'],
                trans['transaction_time'],
                f"{curr} {trans['amount']:,.0f}",
                trans['note'] or '-'
            ))
        
        tk.Button(popup, text="[ DOWNLOAD CSV ]", font=FONTS["button"], bg=COLORS["info"],
                 fg=COLORS["text_primary"], relief=tk.FLAT, bd=0, padx=20, pady=8,
                 command=lambda: export_item_transactions_to_csv(item['item_name'], transactions)).pack(pady=10)
    
    def show_all_transactions_popup(self):
        transactions = get_all_transactions()
        
        popup = tk.Toplevel(self.root)
        popup.title("ALL TRANSACTIONS")
        popup.geometry("750x550")
        popup.configure(bg=COLORS["bg_main"])
        
        tk.Label(popup, text="ALL TRANSACTIONS - GLOBAL VIEW", font=FONTS["heading"],
                bg=COLORS["primary"], fg=COLORS["text_primary"], padx=20, pady=10).pack(fill=tk.X)
        
        total = sum(t['amount'] for t in transactions)
        tk.Label(popup, text=f"Total: {len(transactions)} Transactions | Amount: Rs {total:,.0f}",
                font=FONTS["normal"], bg=COLORS["bg_card"], padx=20, pady=10).pack(fill=tk.X)
        
        list_frame = tk.Frame(popup, bg=COLORS["bg_main"])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        cols = ('date', 'time', 'item', 'amount', 'note')
        tree = ttk.Treeview(list_frame, columns=cols, show='headings')
        
        for col in cols:
            tree.heading(col, text=col.capitalize())
        
        tree.column('date', width=90)
        tree.column('time', width=70)
        tree.column('item', width=120)
        tree.column('amount', width=100)
        tree.column('note', width=180)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        for trans in transactions:
            tree.insert('', tk.END, values=(
                trans['transaction_date'],
                trans['transaction_time'],
                trans['item_name'],
                f"{trans['currency']} {trans['amount']:,.0f}",
                trans['note'] or '-'
            ))
        
        tk.Button(popup, text="[ DOWNLOAD CSV ]", font=FONTS["button"], bg=COLORS["info"],
                 fg=COLORS["text_primary"], relief=tk.FLAT, bd=0, padx=20, pady=8,
                 command=lambda: export_all_transactions_to_csv(transactions)).pack(pady=10)
    
    def download_csv(self):
        try:
            transactions = get_all_transactions()
            export_all_transactions_to_csv(transactions)
        except Exception as e:
            messagebox.showerror("Error", str(e))


# ============ MAIN ============

def main():
    from database import initialize_database
    initialize_database()
    
    root = tk.Tk()
    app = WListApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: root.destroy())
    root.bind('<Escape>', lambda e: root.attributes('-fullscreen', False))
    root.mainloop()

if __name__ == "__main__":
    main()
