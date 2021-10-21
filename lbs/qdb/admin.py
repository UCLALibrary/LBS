from django.contrib import admin
from .models import Account, Recipient, Staff, Unit


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email')
    ordering = ('name',)
    search_fields = ('name', 'email')


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    ordering = ('name',)
    search_fields = ('name',)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('account', 'title', 'cost_center')
    ordering = ('title',)
    search_fields = ('title',)


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ('recipient_id', 'name', 'unit_id', 'unit', 'role')
    ordering = ('recipient_id', 'role',)

    def name(self, obj):
        result = Staff.objects.filter(staff_id=getattr(obj, "recipient_id"))[0]
        return result

    def unit(self, obj):
        result = Staff.objects.filter(unit_id=getattr(obj, "recipient_id"))[0]
        return result
