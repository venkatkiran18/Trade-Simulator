
from supabase_client import get_supabase_client


INITIAL_CASH = 99999.0


def initialize_user_database(user_id):
    # User accounts are initialized in Supabase during registration.
    pass


def load_account(user_id):
    client = get_supabase_client()

    response = (
        client.table("accounts")
        .select("virtual_cash")
        .eq("user_id", user_id)
        .single()
        .execute()
    )

    return float(response.data["virtual_cash"])


def load_portfolio(user_id):
    client = get_supabase_client()

    response = (
        client.table("portfolios")
        .select("company,quantity")
        .eq("user_id", user_id)
        .execute()
    )

    return {
        row["company"]: int(row["quantity"])
        for row in response.data
    }


def load_trades(user_id):
    client = get_supabase_client()

    response = (
        client.table("trades")
        .select("company,action,quantity,price,trade_time")
        .eq("user_id", user_id)
        .order("id", desc=True)
        .execute()
    )

    return [
        (
            row["company"],
            row["action"],
            int(row["quantity"]),
            float(row["price"]),
            row["trade_time"]
        )
        for row in response.data
    ]


def execute_trade(user_id, company, action, quantity, price):
    if action not in ("Buy", "Sell") or quantity <= 0 or price <= 0:
        raise ValueError("Invalid trade details.")

    client = get_supabase_client()

    response = client.rpc(
        "execute_virtual_trade",
        {
            "p_user_id": user_id,
            "p_company": company,
            "p_action": action,
            "p_quantity": quantity,
            "p_price": price
        }
    ).execute()

    result = response.data[0]

    return float(result["virtual_cash"]), int(result["quantity"])


def load_average_costs(user_id):
    client = get_supabase_client()

    response = (
        client.table("trades")
        .select("company,action,quantity,price")
        .eq("user_id", user_id)
        .order("id")
        .execute()
    )

    holdings = {}

    for row in response.data:
        company = row["company"]
        action = row["action"]
        qty = int(row["quantity"])
        price = float(row["price"])

        item = holdings.setdefault(
            company,
            {"quantity": 0, "cost": 0.0}
        )

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

    return {
        name: item["cost"] / item["quantity"]
        for name, item in holdings.items()
        if item["quantity"] > 0
    }


def calculate_realized_profit_loss(user_id):
    client = get_supabase_client()

    response = (
        client.table("trades")
        .select("company,action,quantity,price")
        .eq("user_id", user_id)
        .order("id")
        .execute()
    )

    holdings = {}
    realized = 0.0

    for row in response.data:
        company = row["company"]
        action = row["action"]
        qty = int(row["quantity"])
        price = float(row["price"])

        item = holdings.setdefault(
            company,
            {"quantity": 0, "cost": 0.0}
        )

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
