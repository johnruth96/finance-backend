from rest_framework import serializers

from finance.models import Record
from transactions.models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    account = serializers.StringRelatedField()
    records = serializers.PrimaryKeyRelatedField(many=True, queryset=Record.objects.all())

    class Meta:
        model = Transaction
        fields = '__all__'
