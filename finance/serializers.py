from rest_framework import serializers

from finance.models import Record, Contract, Category, Account
from transactions.models import Transaction


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'


class RecordSerializer(serializers.ModelSerializer):
    transactions = serializers.PrimaryKeyRelatedField(queryset=Transaction.objects.all(), many=True)

    class Meta:
        model = Record
        fields = '__all__'
        extra_kwargs = {
            "date": dict(input_formats=[
                "%d.%m.%Y",
                "%Y-%m-%d",
            ]),
        }


# TODO: Fix typo in 'cancelation'
class ContractSerializer(serializers.ModelSerializer):
    # Payment information
    next_payment_date = serializers.DateField(source='get_next_payment_date', read_only=True)
    amount_per_year = serializers.FloatField(source='get_amount_yearly', read_only=True)

    # Contract information
    is_cancelation_shortly = serializers.BooleanField(read_only=True)
    next_extension_date = serializers.DateField(source='get_next_extension_date', read_only=True)
    next_cancelation_date = serializers.DateField(source='get_next_cancelation_date', read_only=True)

    class Meta:
        model = Contract
        fields = '__all__'
        extra_kwargs = dict(
            date_start=dict(input_formats=["%d.%m.%Y"]),
            payment_date=dict(input_formats=["%d.%m.%Y"]),
        )


class CategorySerializer(serializers.ModelSerializer):
    color = serializers.CharField(source='get_color', read_only=True)

    class Meta:
        model = Category
        fields = '__all__'
