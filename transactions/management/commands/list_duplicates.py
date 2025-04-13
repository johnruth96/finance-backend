import pprint

from django.core.management import BaseCommand
from django.db.models import Count

from transactions.models import Transaction


class Command(BaseCommand):
    def handle(self, *args, **options):
        qs = Transaction.objects.values("value_date", "purpose", "amount").annotate(count=Count("*"))
        duplicates = qs.filter(count__gte=2)
        pprint.pprint(list(duplicates))
