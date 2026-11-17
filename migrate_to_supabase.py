
import sqlite3
from pathlib import Path
from supabase_client import get_supabase_client

ROOT = Path(__file__).resolve().parent
AUTH_DB = ROOT / "users.db"

def migrate():
    client = get_supabase_client()

    # Read existing registered accounts
    with sqlite3.connect(AUTH_DB) as conn:
        users = conn.execute("""
            SELECT id, email, password_salt, password_hash, db_filename
            FROM users
        """).fetchall()

    if not users:
        print("No registered accounts found.")
        return

    # Safety check: do not overwrite existing Supabase data
    existing = client.table("users").select("id").limit(1).execute()
    if existing.data:
        print("Migration stopped: Supabase users table is not empty.")
        print("No data was migrated.")
        return

    for user_id, email, salt, password_hash, db_filename in users:
        db_path = ROOT / db_filename

        if not db_path.exists():
            raise FileNotFoundError(
                f"Trading database missing for account {email}"
            )

        # Preserve the existing password hash and salt
        client.table("users").insert({
            "id": user_id,
            "email": email,
            "password_salt": bytes(salt).hex(),
            "password_hash": bytes(password_hash).hex()
        }).execute()

        with sqlite3.connect(db_path) as conn:
            cash = conn.execute(
                "SELECT virtual_cash FROM account WHERE id=1"
            ).fetchone()[0]

            portfolio = conn.execute(
                "SELECT company, quantity FROM portfolio WHERE quantity > 0"
            ).fetchall()

            trades = conn.execute("""
                SELECT company, action, quantity, price, trade_time
                FROM trades ORDER BY id ASC
            """).fetchall()

        client.table("accounts").insert({
            "user_id": user_id,
            "virtual_cash": float(cash)
        }).execute()

        if portfolio:
            client.table("portfolios").insert([
                {
                    "user_id": user_id,
                    "company": company,
                    "quantity": quantity
                }
                for company, quantity in portfolio
            ]).execute()

        if trades:
            client.table("trades").insert([
                {
                    "user_id": user_id,
                    "company": company,
                    "action": action,
                    "quantity": quantity,
                    "price": float(price),
                    "trade_time": trade_time
                }
                for company, action, quantity, price, trade_time in trades
            ]).execute()

        print("Migrated one account successfully.")

    print("Migration completed!")

if __name__ == "__main__":
    migrate()
