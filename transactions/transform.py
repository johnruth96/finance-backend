from typing import Optional

from finance.models import Record
from transactions.models import Transaction


class Transformer:
    def transform(self, transaction: Transaction) -> Optional[Record]:
        return None
