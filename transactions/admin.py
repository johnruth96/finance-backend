from django.contrib import admin

from transactions.models import Account, Transaction

admin.register(Account)
admin.register(Transaction)
