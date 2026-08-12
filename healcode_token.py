import secrets


TOKEN_PREFIX = "heal_"
TOKEN_BYTES = 32


def generate_healcode_token() -> str:
    """
    Generate a cryptographically secure HealCode token.

    Example:
        heal_7f8c9a...
    """
    random_part = secrets.token_urlsafe(TOKEN_BYTES)
    return f"{TOKEN_PREFIX}{random_part}"