import csv
import logging
from datetime import datetime
from io import StringIO
from urllib.request import urlopen

from django.db import transaction
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, APIException
from rest_framework.response import Response

from finance.models import Record
from transactions.models import Transaction, Account
from transactions.serializers import TransactionSerializer

logger = logging.getLogger()


def import_csv(reader: csv.reader):
    reading_payload = False
    contains_saldo = False

    iban = None
    name = None

    transactions = []
    for row in reader:
        if not row:
            continue

        if row[0] == "IBAN":
            iban = row[1].replace(" ", "").strip()

        if row[0] == "Kontoname":
            name = row[1]

        if row[0] == "Saldo":
            contains_saldo = True
            logger.debug("File contains 'Saldo'")

        if row[0] == "Buchung":
            reading_payload = True
            continue

        if reading_payload:
            amount_str = row[7] if contains_saldo else row[5]
            currency = row[8] if contains_saldo else row[6]

            transactions.append(dict(
                booking_date=datetime.strptime(row[0], "%d.%m.%Y"),
                value_date=datetime.strptime(row[1], "%d.%m.%Y"),
                creditor=row[2],
                transaction_type=row[3],
                purpose=row[4],
                amount=float(amount_str.replace(".", "").replace(",", ".")),
                currency=currency,
            ))

    with transaction.atomic():
        try:
            account = Account.objects.get(iban=iban)
        except Account.DoesNotExist:
            account = Account.objects.create(
                iban=iban,
                name=name,
            )

        num_created = 0
        for transaction_dict in transactions:
            _, created = Transaction.objects.get_or_create(
                account=account,
                **transaction_dict,
            )

            if created:
                num_created += 1

        logger.debug(f"Done. Added {num_created}/{len(transactions)} transactions")


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    @action(methods=["POST"], detail=True)
    def hide(self, request, pk=None):
        t = Transaction.objects.get(pk=pk)

        if t.is_imported:
            raise APIException("Transaction is imported.")

        t.is_ignored = True
        t.save()

        return Response(data=TransactionSerializer(t).data)

    @action(methods=["POST"], detail=True)
    def show(self, request, pk=None):
        t = Transaction.objects.get(pk=pk)

        if not t.is_ignored:
            raise APIException("Transaction is not ignored.")

        t.is_ignored = False
        t.save()

        return Response(data=TransactionSerializer(t).data)

    @action(methods=["POST"], detail=True)
    def bookmark(self, request, pk=None):
        t = Transaction.objects.get(pk=pk)
        t.is_highlighted = True
        t.save()
        return Response(data=TransactionSerializer(t).data)

    @action(methods=["POST"], detail=True)
    def unbookmark(self, request, pk=None):
        t = Transaction.objects.get(pk=pk)
        t.is_highlighted = False
        t.save()
        return Response(data=TransactionSerializer(t).data)

    @action(methods=["POST"], detail=False)
    def counter_booking(self, request, pk=None):
        if len(request.data) != 2:
            raise ValidationError()

        pk_a = request.data[0]
        pk_b = request.data[1]

        tr_a = Transaction.objects.get(pk=pk_a)
        tr_b = Transaction.objects.get(pk=pk_b)

        if tr_a.account != tr_b.account:
            raise ValidationError()

        tr_a.is_counter_to = tr_b
        tr_b.is_counter_to = tr_a

        tr_a.save()
        tr_b.save()

        return Response(status=200)

    @action(methods=["POST"], detail=True)
    def records(self, request, pk=None):
        t = Transaction.objects.get(pk=pk)
        records = Record.objects.filter(pk__in=request.data)
        t.records.set(records)

        return Response(data=TransactionSerializer(t).data)

    @action(methods=["POST"], detail=False, url_path="import")
    def import_csv(self, request, pk=None):
        logger.debug(f"Process files: {request.data}")

        # Except: CSV file with delimiter ";"
        if not isinstance(request.data, list):
            raise ValidationError()

        with transaction.atomic():
            for data_uri in request.data:
                with urlopen(data_uri) as response:
                    data = response.read()

                f = StringIO(data.decode("iso-8859-1"))
                reader = csv.reader(f, delimiter=";")
                import_csv(reader)

        return Response(status=204)
