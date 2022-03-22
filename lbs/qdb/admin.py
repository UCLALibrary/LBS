from django.utils.html import mark_safe
from django.contrib import admin
from .models import Account, Recipient, Staff, Unit


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email')
    ordering = ('name',)
    search_fields = ('name', 'email')


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'unit_aul', 'unit_head', 'unit_assoc',)
    ordering = ('name',)
    search_fields = ('name',)

    def unit_aul(self, obj):
        if(Recipient.objects.filter(unit_id=getattr(obj, "id")) & Recipient.objects.filter(role="aul")):
            unit_aul_num = (Recipient.objects.filter(unit_id=getattr(
                obj, "id")) & Recipient.objects.filter(role="aul")).values_list('recipient_id', flat=True)

            unit_aul = Staff.objects.filter(
                id=unit_aul_num[0]).values_list('name', flat=True)

            aul_id = (Recipient.objects.filter(unit_id=getattr(
                obj, "id")) & Recipient.objects.filter(role="aul")).values_list('id', flat=True)

            result = "<a href=../../../admin/qdb/recipient/" + \
                str(aul_id[0]) + "/change/?_changelist_filters=o%3D1.6>" + \
                str(unit_aul[0]) + "</a>"
        else:
            result = "<a href=../../../admin/qdb/recipient/add/>-----</a>"
        return mark_safe(result)

    def unit_head(self, obj):
        if(Recipient.objects.filter(unit_id=getattr(obj, "id")) & Recipient.objects.filter(role="head")):
            unit_head_num = (Recipient.objects.filter(unit_id=getattr(
                obj, "id")) & Recipient.objects.filter(role="head")).values_list('recipient_id', flat=True)

            unit_head = Staff.objects.filter(
                id=unit_head_num[0]).values_list('name', flat=True)

            head_id = (Recipient.objects.filter(unit_id=getattr(
                obj, "id")) & Recipient.objects.filter(role="head")).values_list('id', flat=True)

            result = "<a href=../../../admin/qdb/recipient/" + \
                str(head_id[0]) + "/change/?_changelist_filters=o%3D1.6>" + \
                str(unit_head[0]) + "</a>"
        else:
            result = "<a href=../../../admin/qdb/recipient/add/>-----</a>"
        return mark_safe(result)

    def unit_assoc(self, obj):
        init_id_num = getattr(obj, "id")
        if(Recipient.objects.filter(unit_id=getattr(obj, "id")) & Recipient.objects.filter(role="assoc")):
            unit_assoc_num = (Recipient.objects.filter(unit_id=getattr(
                obj, "id")) & Recipient.objects.filter(role="assoc")).values_list('recipient_id', flat=True)

            unit_assoc = Staff.objects.filter(
                id=unit_assoc_num[0]).values_list('name', flat=True)

            assoc_id = (Recipient.objects.filter(unit_id=getattr(
                obj, "id")) & Recipient.objects.filter(role="assoc")).values_list('id', flat=True)

            result = "<a href=../../../admin/qdb/recipient/" + \
                str(assoc_id[0]) + "/change/?_changelist_filters=o%3D1.6>" + \
                str(unit_assoc[0]) + "</a>"
        else:
            result = "<a href=../../../admin/qdb/recipient/add/?unit=" + \
                str(init_id_num) + ">-----</a>"
        return mark_safe(result)


@ admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('account', 'title', 'cost_center')
    ordering = ('title',)
    search_fields = ('title',)


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ('recipient_id', 'name', 'unit_id', 'unit', 'role')
    ordering = ('recipient_id', 'role',)

    def name(self, obj):
        result = Staff.objects.filter(id=getattr(obj, "recipient_id"))[0]
        return result

    def unit(self, obj):
        result = Staff.objects.filter(unit_id=getattr(obj, "recipient_id"))[0]
        return result
