from django.utils.html import mark_safe
from django.contrib import admin
from .models import Account, Recipient, Staff, Unit


# create page to display units
@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email')
    ordering = ('name',)
    search_fields = ('name', 'email')


# create page to display units, add links to reipients to allow editing of recipient
@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    # display these columns with id, name from db, others are generated below
    list_display = ('id', 'name', 'unit_aul', 'unit_head', 'unit_assoc',)
    ordering = ('name',)
    search_fields = ('name',)

    def unit_aul(self, obj):
        result = edit_recip_link(obj, "aul")
        return mark_safe(result)

    def unit_head(self, obj):
        result = edit_recip_link(obj, "head")
        return mark_safe(result)

    # dhc: put these into a for loop
    def unit_assoc(self, obj):
        result = edit_recip_link(obj, "assoc")
        return mark_safe(result)


# create page to display accounts
@ admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('account', 'title', 'cost_center')
    ordering = ('title',)
    search_fields = ('title',)

# create page to display recipients through table


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

# given unit, add aul, head and assoc recipients as links to edit the recipient


def edit_recip_link(obj, unitRecipTitle):
    # if the current unit has a passed-in value which matches either aul, head, or assoc
    if(Recipient.objects.filter(unit_id=getattr(obj, "id")) & Recipient.objects.filter(role=unitRecipTitle)):
        # id from the staff table of the staff member who is the unitRecipTitle of the current unit
        staff_id_unitRecipTitle = (Recipient.objects.filter(unit_id=getattr(
            obj, "id")) & Recipient.objects.filter(role=unitRecipTitle)).values_list('recipient_id', flat=True)
        # name from the staff table of the staff member who is the unitRecipTitle of the current unit
        staff_name_unitRecipTitle = Staff.objects.filter(
            id=staff_id_unitRecipTitle[0]).values_list('name', flat=True)
        # id from the unit table of the current unit which has the staff member as the unitRecipTitle
        unit_id_unitRecipTitle = (Recipient.objects.filter(unit_id=getattr(
            obj, "id")) & Recipient.objects.filter(role=unitRecipTitle)).values_list('id', flat=True)
        # return a link to manage the unit and role of the staff member currently designated unitRecipTitle of the current unit
        result = "<a href=../../../admin/qdb/recipient/" + \
            str(unit_id_unitRecipTitle[0]) + "/change/>" + \
            str(staff_name_unitRecipTitle[0]) + "</a>"
    else:
        # id from the unit table of the current unit
        unit_id_num = getattr(obj, "id")
        # return a link to add a recipient (staff member) and role to the current unit
        result = "<a href=../../../admin/qdb/recipient/add/?unit=" + \
            str(unit_id_num) + ">-----</a>"

    return(result)
