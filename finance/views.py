from django.db.models import Count
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from finance.models import Record, Contract, Category, Account
from finance.serializers import RecordSerializer, ContractSerializer, CategorySerializer, AccountSerializer
from transactions.models import Transaction
from transactions.serializers import TransactionSerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'pageSize'
    max_page_size = 1000


class AccountViewSet(viewsets.ReadOnlyModelViewSet):
    model = Account
    serializer_class = AccountSerializer
    queryset = Account.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class RecordViewSet(viewsets.ModelViewSet):
    model = Record
    serializer_class = RecordSerializer
    queryset = Record.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    ALLOWED_LOOKUPS = (
        "id",
        "account",
        "date__gte",
        "date__gt",
        "date__lte",
        "date__lt",
        "date",
        "date_created__gte",
        "date_created__gt",
        "date_created__lte",
        "date_created__lt",
        "date_created",
        "category",
        "contract",
        "subject",
        "subject__icontains",
        "subject__istartswith",
        "subject__iendswith",
        "transaction_count",
        "transaction_count__gte",
        "transaction_count__gt",
        "transaction_count__lte",
        "transaction_count__lt",
    )

    @action(detail=True)
    def transactions(self, request, pk=None):
        record = self.get_object()
        transactions = record.transactions.all()
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'], url_path=r'transactions/(?P<transaction_id>\d+)')
    def link_transaction(self, request, pk=None, transaction_id=None):
        record = self.get_object()

        try:
            transaction = Transaction.objects.get(pk=transaction_id)
            record.transactions.add(transaction)
            return Response(status=status.HTTP_201_CREATED)
        except Transaction.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND
            )

    @link_transaction.mapping.delete
    def unlink_transaction(self, request, pk=None, transaction_id=None):
        record = self.get_object()

        try:
            transaction = Transaction.objects.get(pk=transaction_id)

            if transaction in record.transactions.all():
                record.transactions.remove(transaction)
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        except Transaction.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=False)
    def subjects(self, request):
        query = request.query_params.get("query", "")
        qs = Record.objects.all()
        if query != "":
            qs = qs.filter(subject__startswith=query)
        qs = qs.values_list("subject", "category", "contract").distinct().order_by()
        response = Response(data=qs)
        return response

    def get_queryset(self):
        qs = super().get_queryset()

        # Sorting
        order_by = self.request.query_params.getlist("sortBy")
        qs = qs.order_by(*order_by)

        # Filtering
        qs = qs.annotate(transaction_count=Count('transactions'))
        for lookup in self.ALLOWED_LOOKUPS:
            value = self.request.query_params.get(lookup)
            if value:
                qs = qs.filter(**{lookup: value})

        # Quick filter
        query = self.request.query_params.get("q", "")
        if query:
            qs = qs.filter(subject__icontains=query)

        return qs


class ContractViewSet(viewsets.ModelViewSet):
    model = Contract
    serializer_class = ContractSerializer
    queryset = Contract.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class CategoryViewSet(viewsets.ModelViewSet):
    model = Category
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = [permissions.IsAuthenticated]
