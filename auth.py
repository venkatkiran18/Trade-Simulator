
import hashlib
import hmac
import secrets
import uuid

from supabase_client import get_supabase_client

ITERATIONS = 310_000


def _hash_password(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        ITERATIONS
    )


def register(email, password):
    email = email.strip().lower()

    if "@" not in email or "." not in email.split("@")[-1]:
        raise ValueError("Enter a valid email address.")

    if len(password) < 10:
        raise ValueError("Use a password with at least 10 characters.")

    salt = secrets.token_bytes(16)
    digest = _hash_password(password, salt)
    user_id = str(uuid.uuid4())

    client = get_supabase_client()

    try:
        client.table("users").insert({
            "id": user_id,
            "email": email,
            "password_salt": salt.hex(),
            "password_hash": digest.hex()
        }).execute()

        client.table("accounts").insert({
            "user_id": user_id,
            "virtual_cash": 99999.00
        }).execute()

    except Exception:
        # Avoid leaving an incomplete account if registration fails.
        client.table("users").delete().eq("id", user_id).execute()
        raise

    return {
        "id": user_id,
        "email": email
    }


def login(email, password):
    client = get_supabase_client()

    response = (
        client.table("users")
        .select("id,email,password_salt,password_hash")
        .eq("email", email.strip().lower())
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    row = response.data[0]

    salt = bytes.fromhex(row["password_salt"])
    expected = bytes.fromhex(row["password_hash"])

    actual = _hash_password(password, salt)

    if not hmac.compare_digest(actual, expected):
        return None

    return {
        "id": row["id"],
        "email": row["email"]
    }


def initialize_auth_db():
    # Supabase tables were created in the Supabase project.
    pass
