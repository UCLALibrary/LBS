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
        # if the current unit has an aul
        if(Recipient.objects.filter(unit_id=getattr(obj, "id")) & Recipient.objects.filter(role="aul")):

            # id from the staff table of the staff member who is the aul of the current unit
            staff_id_aul = (Recipient.objects.filter(unit_id=getattr(
                obj, "id")) & Recipient.objects.filter(role="aul")).values_list('recipient_id', flat=True)

            # name from the staff table of the staff member who is the aul of the current unit
            staff_name_aul = Staff.objects.filter(
                id=staff_id_aul[0]).values_list('name', flat=True)

            # id from the unit table of the current unit which has the staff member as the aul
            unit_id_aul = (Recipient.objects.filter(unit_id=getattr(
                obj, "id")) & Recipient.objects.filter(role="aul")).values_list('id', flat=True)

            # return a link to manage the unit and role of the staff member currently designated aul of the current unit
            result = "<a href=../../../admin/qdb/recipient/" + \
                str(unit_id_aul[0]) + "/change/>" + \
                str(staff_name_aul[0]) + "</a>"
        else:
            # id from the unit table of the current unit
            unit_id_num = getattr(obj, "id")
            # return a link to add a recipient (staff member) and role to the current unit
            result = "<a href=../../../admin/qdb/recipient/add/?unit=" + \
                str(unit_id_num) + ">-----</a>"
        return mark_safe(result)

    def unit_head(self, obj):
        # if the current unit has an head
        if(Recipient.objects.filter(unit_id=getattr(obj, "id")) & Recipient.objects.filter(role="head")):

            # id from the staff table of the staff member who is the head of the current unit
            staff_id_head = (Recipient.objects.filter(unit_id=getattr(
                obj, "id")) & Recipient.objects.filter(role="head")).values_list('recipient_id', flat=True)

            # name from the staff table of the staff member who is the head of the current unit
            staff_name_head = Staff.objects.filter(
                id=staff_id_head[0]).values_list('name', flat=True)

            # id from the unit table of the current unit which has the staff member as the head
            unit_id_head = (Recipient.objects.filter(unit_id=getattr(
                obj, "id")) & Recipient.objects.filter(role="head")).values_list('id', flat=True)

            # return a link to manage the unit and role of the staff member currently designated head of the current unit
            result = "<a href=../../../admin/qdb/recipient/" + \
                str(unit_id_head[0]) + "/change/>" + \
                str(staff_name_head[0]) + "</a>"
        else:
            # id from the unit table of the current unit
            unit_id_num = getattr(obj, "id")
            # return a link to add a recipient (staff member) and role to the current unit
            result = "<a href=../../../admin/qdb/recipient/add/?unit=" + \
                str(unit_id_num) + ">-----</a>"
        return mark_safe(result)

#    def unit_head(self, obj):
#        unit_id_num = getattr(obj, "id")
#        if(Recipient.objects.filter(unit_id=getattr(obj, "id")) & Recipient.objects.filter(role="head")):
#            unit_head_num = (Recipient.objects.filter(unit_id=getattr(
#                obj, "id")) & Recipient.objects.filter(role="head")).values_list('recipient_id', flat=True)
#
#            unit_head = Staff.objects.filter(
#                id=unit_head_num[0]).values_list('name', flat=True)
#
#            head_id = (Recipient.objects.filter(unit_id=getattr(
#                obj, "id")) & Recipient.objects.filter(role="head")).values_list('id', flat=True)
#
#            result = "<a href=../../../admin/qdb/recipient/" + \
#                str(head_id[0]) + "/change/?_changelist_filters=o%3D1.6>" + \
#                str(unit_head[0]) + "</a>"
#        else:
#            result = "<a href=../../../admin/qdb/recipient/add/?unit=" + \
#                str(unit_id_num) + ">-----</a>"
#        return mark_safe(result)

    def unit_assoc(self, obj):
        unit_id_num = getattr(obj, "id")
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
                str(unit_id_num) + ">-----</a>"
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
