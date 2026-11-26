"""Verifies password hashes created by Django (Financez), without needing Django."""

import base64
import hashlib
import hmac

ALGORITHM = "pbkdf2_sha256"  # Django's default hasher


def verify_password(password, encoded):
    try:
        algorithm, iterations, salt, expected = encoded.split("$")
        if algorithm != ALGORITHM:
            return False
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), int(iterations))
    except ValueError:
        return False
    return hmac.compare_digest(base64.b64encode(digest), expected.encode())
