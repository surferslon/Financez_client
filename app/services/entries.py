import logging

from app.domain.entry import Entry, InvalidEntry

logger = logging.getLogger(__name__)


class EntryService:
    def __init__(self, repository):
        self.repository = repository

    def add(self, user, date, acc_dr, acc_cr, currency, total, comment):
        """Validates and stores a new entry of the user, raises InvalidEntry."""
        entry = Entry.new(date, acc_dr, acc_cr, currency, total, comment)
        account_ids = {account["id"] for account in user.accounts}
        currency_ids = {item["id"] for item in user.currencies}
        if entry.acc_dr not in account_ids or entry.acc_cr not in account_ids or entry.currency not in currency_ids:
            raise InvalidEntry("unknown account or currency")
        self.repository.add(user.username, entry)
        logger.info("Entry %s added by %r", entry.id, user.username)
        return entry

    def pending(self, username):
        """Entries not yet picked up by Financez, oldest first."""
        return self.repository.list(username)

    def remove(self, username, ids):
        self.repository.delete(username, ids)
        logger.info("Removed entries of %r: %s", username, ", ".join(map(str, ids)))
