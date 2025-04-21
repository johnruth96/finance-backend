from django.db.models import Count
from django_filters import rest_framework as filters

from transactions.models import Transaction


class RecordCountFilter(filters.NumberFilter):
    def __init__(self, **kwargs):
        field_name = "record_count"
        super().__init__(field_name=field_name, **kwargs)

    def filter(self, qs, value):
        qs = qs.annotate(record_count=Count('records'))
        return super().filter(qs, value)


class TransactionFilter(filters.FilterSet):
    account__istartswith = filters.CharFilter(field_name="account__iban", lookup_expr="istartswith")

    is_duplicate = filters.BooleanFilter(field_name="is_counter_to", lookup_expr="isnull", exclude=True)

    record_count = RecordCountFilter()
    record_count__gt = RecordCountFilter(lookup_expr="gt")
    record_count__gte = RecordCountFilter(lookup_expr="gte")
    record_count__lt = RecordCountFilter(lookup_expr="lt")
    record_count__lte = RecordCountFilter(lookup_expr="lte")

    class Meta:
        model = Transaction
        fields = {
            "booking_date": ["exact", "gte", "lte", "gt", "lt", "isnull"],
            "creditor": ["exact", "icontains", "istartswith", "iendswith"],
            "transaction_type": ["exact", "icontains", "istartswith", "iendswith"],
            "purpose": ["exact", "icontains", "istartswith", "iendswith"],
            "amount": ["exact", "gte", "lte", "gt", "lt"],
            "is_highlighted": ["exact"],
        }
