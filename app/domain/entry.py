import uuid
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation

# Same limits as Entry in Financez
TOTAL_LIMIT = Decimal(10**12)
TOTAL_STEP = Decimal("0.001")
COMMENT_LENGTH = 1024


class InvalidEntry(ValueError):
    pass


@dataclass(frozen=True)
class Entry:
    id: str
    date: str
    acc_dr: int
    acc_cr: int
    currency: int
    total: Decimal
    comment: str

    @classmethod
    def new(cls, date_, acc_dr, acc_cr, currency, total, comment):
        """Builds a new entry from user input (strings)."""
        try:
            parsed_total = Decimal(total.strip().replace(",", "."))
            if not parsed_total.is_finite() or abs(parsed_total) >= TOTAL_LIMIT or parsed_total != parsed_total.quantize(TOTAL_STEP):
                raise InvalidEntry("total")
            return cls(
                id=str(uuid.uuid4()),
                date=date.fromisoformat(date_).isoformat(),
                acc_dr=int(acc_dr),
                acc_cr=int(acc_cr),
                currency=int(currency),
                total=parsed_total,
                comment=comment.strip()[:COMMENT_LENGTH],
            )
        except (ValueError, InvalidOperation) as error:
            raise InvalidEntry(str(error)) from error
