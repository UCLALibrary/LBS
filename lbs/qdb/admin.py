from django.contrib import admin
from .models import Account, Recipient, Staff, Unit


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    pass


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    pass


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    pass


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    pass
