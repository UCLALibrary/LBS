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

    # one method per list item for unit_aul, unit_head, unit_assoc
    def unit_aul(self, obj):
        result = mark_safe(get_recipient_link(obj, "aul"))
        return result

    def unit_head(self, obj):
        result = mark_safe(get_recipient_link(obj, "head"))
        return result

    # dhc: put these into a for loop
    def unit_assoc(self, obj):
        result = mark_safe(get_recipient_link(obj, "assoc"))
        return result


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
def get_recipient_link(obj, role):
    # if the current unit has a passed-in value which matches either aul, head, or assoc
    if(Recipient.objects.filter(unit_id=getattr(
            obj, "id"), role=role)):

        # id from the staff table of the staff member who has the role of the current unit
        staff_id_role = get_recipient_list(
            obj, role, 'recipient_id')

        # id from the unit table of the current unit which has the staff member who has the role of the current unit
        unit_id_role = get_recipient_list(
            obj, role, 'id')

        # name from the staff table of the staff member who has the role of the current unit
        staff_name = Staff.objects.filter(
            id=staff_id_role[0]).values_list('name', flat=True)  # 70

        # return a link to manage the unit and role of the staff member who has the role of the current unit
        result = "<a href=../../../admin/qdb/recipient/" + \
            str(unit_id_role[0]) + "/change/>" + \
            str(staff_name[0]) + "</a>"
        return result
    else:
        # id from the unit table of the current unit
        unit_id_num = getattr(obj, "id")

        # return a link to add a recipient (staff member) and role to the current unit which currently has none
        result = "<a href=../../../admin/qdb/recipient/add/?unit=" + \
            str(unit_id_num) + ">-----</a>"
        return result


# return id given recipient type (aul, head or assoc) and column name of the value needed
def get_recipient_list(obj, recipient_type, value_needed):
    result = Recipient.objects.filter(unit_id=getattr(
        obj, "id"), role=recipient_type).values_list(value_needed, flat=True)
    return result
