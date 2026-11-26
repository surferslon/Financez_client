import hmac


def same(given, expected):
    """Constant-time string comparison."""
    return hmac.compare_digest(given.encode(), expected.encode())
