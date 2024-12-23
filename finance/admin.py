from django.contrib import admin

from finance.models import Record, Category, Contract, Account


class RecordAdmin(admin.ModelAdmin):
    list_display = ('subject', 'date', 'amount', 'account', 'category', 'contract')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'color')


class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'type')


class ContractAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'amount', 'date_start')


admin.site.register(Record, RecordAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(Contract, ContractAdmin)
