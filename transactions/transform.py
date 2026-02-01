import abc

from finance.models import Record
from transactions.models import Transaction


class TransformError(ValueError):
    pass


class Transformer(abc.ABC):
    @abc.abstractmethod
    def transform(self, transaction: Transaction) -> Record:
        """
        :raises TransformError: if Record could no be created
        """
        pass
