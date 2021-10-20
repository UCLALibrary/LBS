from django.contrib import admin
from .models import Accounts, Recipient, Staff, Unit

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    pass

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    pass

@admin.register(Accounts)
class AccountsAdmin(admin.ModelAdmin):
    pass

@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    pass

