import sqlite3
import os
from datetime import datetime

DATABASE_FOLDER = "data"
DATABASE_NAME = "wlist.db"
DATABASE_PATH = os.path.join(DATABASE_FOLDER, DATABASE_NAME)

def ensure_database_folder():
    try:
        if not os.path.exists(DATABASE_FOLDER):
            os.makedirs(DATABASE_FOLDER)
    except Exception as e:
        print(f"Error: {e}")

def get_db_connection():
    try:
        ensure_database_folder()
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Error: {e}")
        raise

def initialize_database():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wishlist_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                icon TEXT NOT NULL DEFAULT 'P',
                item_name TEXT NOT NULL,
                currency TEXT NOT NULL DEFAULT 'Rs',
                target_price REAL NOT NULL,
                total_saved REAL NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                note TEXT,
                currency TEXT NOT NULL DEFAULT 'Rs',
                transaction_date TEXT NOT NULL,
                transaction_time TEXT NOT NULL,
                transaction_month TEXT NOT NULL,
                transaction_year INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (item_id) REFERENCES wishlist_items (id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Database ready!")
    except Exception as e:
        print(f"Error: {e}")

def get_current_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

def get_current_time():
    return datetime.now().strftime("%H:%M:%S")

def get_current_month():
    return datetime.now().strftime("%B")

def get_current_year():
    return datetime.now().year

def create_wishlist_item(icon, item_name, currency, target_price):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        timestamp = get_current_timestamp()
        
        cursor.execute('''
            INSERT INTO wishlist_items 
            (icon, item_name, currency, target_price, total_saved, created_at, updated_at)
            VALUES (?, ?, ?, ?, 0, ?, ?)
        ''', (icon, item_name, currency, target_price, timestamp, timestamp))
        
        item_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return item_id
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_all_wishlist_items():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM wishlist_items ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        items = []
        for row in rows:
            items.append({
                'id': row['id'],
                'icon': row['icon'],
                'item_name': row['item_name'],
                'currency': row['currency'],
                'target_price': row['target_price'],
                'total_saved': row['total_saved'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            })
        return items
    except Exception as e:
        print(f"Error: {e}")
        return []

def get_wishlist_item_by_id(item_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM wishlist_items WHERE id = ?', (item_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row['id'],
                'icon': row['icon'],
                'item_name': row['item_name'],
                'currency': row['currency'],
                'target_price': row['target_price'],
                'total_saved': row['total_saved'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }
        return None
    except Exception as e:
        print(f="Error: {e}")
        return None

def update_wishlist_item_name(item_id, new_name):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        timestamp = get_current_timestamp()
        
        cursor.execute('UPDATE wishlist_items SET item_name = ?, updated_at = ? WHERE id = ?',
                      (new_name, timestamp, item_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def delete_wishlist_item(item_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM transactions WHERE item_id = ?', (item_id,))
        cursor.execute('DELETE FROM wishlist_items WHERE id = ?', (item_id,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def add_transaction(item_id, amount, note, currency):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        timestamp = get_current_timestamp()
        date = get_current_date()
        time = get_current_time()
        month = get_current_month()
        year = get_current_year()
        
        cursor.execute('''
            INSERT INTO transactions 
            (item_id, amount, note, currency, transaction_date, transaction_time, 
             transaction_month, transaction_year, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (item_id, amount, note, currency, date, time, month, year, timestamp))
        
        cursor.execute('SELECT total_saved, target_price FROM wishlist_items WHERE id = ?', (item_id,))
        row = cursor.fetchone()
        
        if row:
            new_total = row['total_saved'] + amount
            if new_total > row['target_price']:
                new_total = row['target_price']
            cursor.execute('UPDATE wishlist_items SET total_saved = ?, updated_at = ? WHERE id = ?',
                          (new_total, timestamp, item_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def get_transactions_by_item_id(item_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM transactions WHERE item_id = ? ORDER BY transaction_date DESC, transaction_time DESC',
                      (item_id,))
        rows = cursor.fetchall()
        conn.close()
        
        transactions = []
        for row in rows:
            transactions.append({
                'id': row['id'],
                'item_id': row['item_id'],
                'amount': row['amount'],
                'note': row['note'],
                'currency': row['currency'],
                'transaction_date': row['transaction_date'],
                'transaction_time': row['transaction_time'],
                'transaction_month': row['transaction_month'],
                'transaction_year': row['transaction_year'],
                'created_at': row['created_at']
            })
        return transactions
    except Exception as e:
        print(f"Error: {e}")
        return []

def get_all_transactions():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT t.*, w.item_name, w.icon, w.currency as item_currency
            FROM transactions t
            JOIN wishlist_items w ON t.item_id = w.id
            ORDER BY t.transaction_date DESC, t.transaction_time DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        transactions = []
        for row in rows:
            transactions.append({
                'id': row['id'],
                'item_id': row['item_id'],
                'item_name': row['item_name'],
                'icon': row['icon'],
                'amount': row['amount'],
                'note': row['note'],
                'currency': row['currency'],
                'transaction_date': row['transaction_date'],
                'transaction_time': row['transaction_time'],
                'transaction_month': row['transaction_month'],
                'transaction_year': row['transaction_year'],
                'created_at': row['created_at']
            })
        return transactions
    except Exception as e:
        print(f"Error: {e}")
        return []

def get_total_savings():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT SUM(total_saved) as total FROM wishlist_items')
        row = cursor.fetchone()
        conn.close()
        return row['total'] if row['total'] else 0.0
    except Exception as e:
        print(f"Error: {e}")
        return 0.0

def calculate_progress_percentage(saved, target):
    try:
        if target <= 0:
            return 0.0
        percentage = (saved / target) * 100
        return min(percentage, 100.0)
    except:
        return 0.0

def get_progress_color(percent):
    if percent >= 100:
        return "#00FF66"
    elif percent >= 76:
        return "#FF0033"
    elif percent >= 51:
        return "#FF6600"
    elif percent >= 26:
        return "#FFAA00"
    else:
        return "#FF0033"

def can_add_amount(item_id, amount):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT target_price, total_saved FROM wishlist_items WHERE id = ?', (item_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            remaining = row['target_price'] - row['total_saved']
            return amount <= remaining
        return False
    except:
        return False
