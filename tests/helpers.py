import base64
import hashlib


def django_hash(password, salt="salt", iterations=1000):
    """A password hash in Django's format (with few iterations to keep tests fast)."""
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), iterations)
    return f"pbkdf2_sha256${iterations}${salt}${base64.b64encode(digest).decode()}"
