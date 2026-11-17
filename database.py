import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
USER_DB_DIR = ROOT 
INITIAL_CASH = 99999.0

def get_connection(db_filename):
    path = USER_DB_DIR / db_filename
    if not path.exists():
        raise FileNotFoundError("The user's trading database was not found.")
    return sqlite3.connect(path)

def initialize_user_database(db_filename):
    USER_DB_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(USER_DB_DIR / db_filename)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS account (
        id INTEGER PRIMARY KEY, virtual_cash REAL NOT NULL)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS portfolio (
        company TEXT PRIMARY KEY, quantity INTEGER NOT NULL DEFAULT 0)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT, company TEXT NOT NULL,
        action TEXT NOT NULL, quantity INTEGER NOT NULL, price REAL NOT NULL,
        trade_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    cur.execute("INSERT OR IGNORE INTO account (id, virtual_cash) VALUES (1, ?)", (INITIAL_CASH,))
    conn.commit()
    conn.close()

def load_account(db_filename):
    with get_connection(db_filename) as conn:
        row = conn.execute("SELECT virtual_cash FROM account WHERE id=1").fetchone()
    return float(row[0]) if row else INITIAL_CASH

def load_portfolio(db_filename):
    with get_connection(db_filename) as conn:
        rows = conn.execute("SELECT company, quantity FROM portfolio").fetchall()
    return {name: int(qty) for name, qty in rows}

def load_trades(db_filename):
    with get_connection(db_filename) as conn:
        return conn.execute("""SELECT company, action, quantity, price, trade_time
            FROM trades ORDER BY id DESC""").fetchall()

def execute_trade(db_filename, company, action, quantity, price):
    if action not in ("Buy", "Sell") or quantity <= 0 or price <= 0:
        raise ValueError("Invalid trade details.")
    cost = quantity * price
    conn = get_connection(db_filename)
    try:
        cur = conn.cursor()
        cur.execute("SELECT virtual_cash FROM account WHERE id=1")
        row = cur.fetchone()
        if row is None:
            raise RuntimeError("Account row is missing.")
        cash = float(row[0])
        cur.execute("SELECT quantity FROM portfolio WHERE company=?", (company,))
        holding_row = cur.fetchone()
        owned = int(holding_row[0]) if holding_row else 0

        if action == "Buy":
            if cost > cash:
                raise ValueError("Insufficient virtual cash.")
            cash -= cost
            new_qty = owned + quantity
        else:
            if quantity > owned:
                raise ValueError("You do not own enough shares to sell.")
            cash += cost
            new_qty = owned - quantity

        cur.execute("UPDATE account SET virtual_cash=? WHERE id=1", (cash,))
        cur.execute("""INSERT INTO portfolio(company, quantity) VALUES (?, ?)
            ON CONFLICT(company) DO UPDATE SET quantity=excluded.quantity""",
            (company, new_qty))
        cur.execute("INSERT INTO trades(company, action, quantity, price) VALUES (?,?,?,?)",
                    (company, action, quantity, price))
        conn.commit()
        return cash, new_qty
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def load_average_costs(db_filename):
    with get_connection(db_filename) as conn:
        rows = conn.execute("""SELECT company, action, quantity, price
            FROM trades ORDER BY id ASC""").fetchall()
    holdings = {}
    for company, action, qty, price in rows:
        item = holdings.setdefault(company, {"quantity": 0, "cost": 0.0})
        if action == "Buy":
            item["quantity"] += qty
            item["cost"] += qty * price
        elif action == "Sell" and item["quantity"] > 0:
            sold = min(qty, item["quantity"])
            avg = item["cost"] / item["quantity"]
            item["quantity"] -= sold
            item["cost"] -= sold * avg
            if item["quantity"] == 0:
                item["cost"] = 0.0
    return {name: item["cost"] / item["quantity"]
            for name, item in holdings.items() if item["quantity"] > 0}

def calculate_realized_profit_loss(db_filename):
    with get_connection(db_filename) as conn:
        rows = conn.execute("""SELECT company, action, quantity, price
            FROM trades ORDER BY id ASC""").fetchall()
    holdings = {}
    realized = 0.0
    for company, action, qty, price in rows:
        item = holdings.setdefault(company, {"quantity": 0, "cost": 0.0})
        if action == "Buy":
            item["quantity"] += qty
            item["cost"] += qty * price
        elif action == "Sell" and item["quantity"] > 0:
            sold = min(qty, item["quantity"])
            avg = item["cost"] / item["quantity"]
            realized += sold * (price - avg)
            item["quantity"] -= sold
            item["cost"] -= sold * avg
            if item["quantity"] == 0:
                item["cost"] = 0.0
    return realized
