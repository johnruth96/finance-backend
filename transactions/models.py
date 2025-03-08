from django.db import models


class Account(models.Model):
    iban = models.CharField(max_length=22)
    name = models.CharField(max_length=1024)

    def __str__(self):
        return self.iban


class Transaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    booking_date = models.DateTimeField()
    value_date = models.DateTimeField()
    creditor = models.TextField()
    amount = models.DecimalField(decimal_places=2, max_digits=8)
    currency = models.CharField(max_length=3)
    transaction_type = models.TextField()
    purpose = models.TextField()

    # Meta data
    date_created = models.DateTimeField(auto_now_add=True)
    is_ignored = models.BooleanField(default=False)
    is_counter_to = models.ForeignKey('transactions.Transaction', on_delete=models.SET_NULL, null=True)
    is_highlighted = models.BooleanField(default=False)

    records = models.ManyToManyField('finance.Record', related_name='transactions')

    @property
    def is_new(self):
        return not self.records.exists() and not self.is_ignored

    @property
    def is_imported(self):
        return self.records.exists() and not self.is_ignored

    class Meta:
        ordering = ('booking_date',)
