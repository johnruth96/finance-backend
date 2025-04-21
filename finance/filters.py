from django.db.models import Count
from django_filters import rest_framework as filters

from finance.models import Record


class TransactionCountFilter(filters.NumberFilter):
    def __init__(self, **kwargs):
        field_name = "transaction_count"
        super().__init__(field_name=field_name, **kwargs)

    def filter(self, qs, value):
        qs = qs.annotate(transaction_count=Count('transactions'))
        return super().filter(qs, value)


class RecordFilter(filters.FilterSet):
    q = filters.CharFilter(field_name="subject", lookup_expr="icontains")

    transaction_count = TransactionCountFilter()
    transaction_count__gt = TransactionCountFilter(lookup_expr="gt")
    transaction_count__gte = TransactionCountFilter(lookup_expr="gte")
    transaction_count__lt = TransactionCountFilter(lookup_expr="lt")
    transaction_count__lte = TransactionCountFilter(lookup_expr="lte")

    class Meta:
        model = Record
        fields = {
            "id": ["exact"],
            "account": ["exact"],
            "date": ["exact", "gte", "lte", "gt", "lt"],
            "date_created": ["exact", "gte", "lte", "gt", "lt"],
            "amount": ["exact", "gte", "lte", "gt", "lt"],
            "category": ["exact"],
            "contract": ["exact"],
            "subject": ["exact", "icontains", "istartswith", "iendswith"],
        }
