import logging

from app.domain.password import ALGORITHM, verify_password
from app.domain.user import User

logger = logging.getLogger(__name__)

# Checked for unknown usernames, so that they take as long to reject as wrong passwords
UNKNOWN_USER_HASH = f"{ALGORITHM}$1000000$unknown$unknown"


class UserService:
    def __init__(self, repository):
        self.repository = repository

    def get(self, username):
        return self.repository.get(username)

    def save(self, username, password_hash, accounts, currencies):
        self.repository.save(User(username, password_hash, accounts, currencies))
        logger.info("Sync: received user %r with %d accounts, %d currencies", username, len(accounts), len(currencies))

    def authenticate(self, username, password):
        """Returns the user if the Financez credentials are correct, otherwise None."""
        user = self.repository.get(username)
        valid = verify_password(password, user.password_hash if user else UNKNOWN_USER_HASH)
        if not (user and valid):
            logger.warning("Failed login for %r", username)
            return None
        logger.info("Login of %r", username)
        return user
