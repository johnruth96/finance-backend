from rest_framework import serializers

from finance.serializers import RecordSerializer
from transactions.models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    account = serializers.StringRelatedField()
    records = RecordSerializer(many=True)

    class Meta:
        model = Transaction
        fields = '__all__'
