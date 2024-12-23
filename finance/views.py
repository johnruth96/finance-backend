from datetime import datetime

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from finance.models import Record, Contract, Category, Account
from finance.serializers import RecordSerializer, ContractSerializer, CategorySerializer, AccountSerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
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

    def get_serializer(self, *args, **kwargs):
        if isinstance(self.request.data, list):
            kwargs.update(many=True)
        return super().get_serializer(*args, **kwargs)

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
        params = dict()

        date_start = self.request.query_params.get("date_start")
        date_end = self.request.query_params.get("date_end")
        category = self.request.query_params.get("category")
        contract = self.request.query_params.get("contract")
        subject = self.request.query_params.get("subject")
        account = self.request.query_params.get("account")

        if date_start:
            params.update(date__gte=datetime.strptime(date_start, "%Y-%m-%d"))
        if date_end:
            params.update(date__lte=datetime.strptime(date_end, "%Y-%m-%d"))
        if category:
            category = Category.objects.get(pk=category)
            params.update(category__in=category.subtree())
        if contract:
            params.update(contract=contract)
        if subject:
            params.update(subject__icontains=subject)
        if account:
            params.update(account=account)
        if params:
            qs = qs.filter(**params)
        return qs

    def paginate_queryset(self, queryset):
        if self.paginator and self.paginator.page_query_param not in self.request.query_params:
            return None
        return super().paginate_queryset(queryset)


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
