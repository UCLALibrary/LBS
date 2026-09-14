from django.contrib import admin
from django.utils.html import format_html
from .models import GeStaff, GeUnit, GeFund, GeRecipient


# Register your models here.
# create page to display GE staff
@admin.register(GeStaff)
class GeStaffAdmin(admin.ModelAdmin):
    list_display = ("name", "email")
    ordering = ("name",)
    search_fields = ("name", "email")


# create page to display GE units
@admin.register(GeUnit)
class GeUnitAdmin(admin.ModelAdmin):
    list_display = ["name", "unit_aul", "unit_head"]
    ordering = ("name",)
    search_fields = ["name"]

    def unit_aul(self, obj):
        result = format_html(get_recipient_link(obj, "aul"))
        return result

    def unit_head(self, obj):
        result = format_html(get_recipient_link(obj, "head"))
        return result


# create page to display GE funds
@admin.register(GeFund)
class GeFundAdmin(admin.ModelAdmin):
    list_display = (
        "account",
        "cost_center",
        "fund",
        "title",
        "manager",
        "mtf_authority",
        "unit",
        "home_unit_dept",
        "projected_annual_income",
        "active",
        "fund_purpose",
        "fund_summary",
        "fund_restriction",
        "general_notes",
        "lbs_notes",
    )
    ordering = ("account",)
    search_fields = ("account", "fund", "title", "unit__name", "home_unit_dept")
    list_filter = ["manager", "mtf_authority", "active"]


@admin.register(GeRecipient)
class GeRecipientAdmin(admin.ModelAdmin):
    list_display = ("get_name", "get_unit", "role")
    ordering = ("recipient__name", "unit__name", "role")
    search_fields = ["recipient__name", "unit__name", "role"]

    @admin.display(description="Name", ordering="recipient__name")
    def get_name(self, recipient):
        return recipient.recipient.name

    @admin.display(description="Unit", ordering="unit__name")
    def get_unit(self, recipient):
        return recipient.unit.name


# Given unit, add aul and head recipients as links to edit the recipient.
def get_recipient_link(obj, role):
    # if the current unit has a passed-in value which matches either aul or head
    if GeRecipient.objects.filter(unit_id=getattr(obj, "id"), role=role):

        # id of the staff member who has the role of the current unit
        staff_id_role = get_recipient_list(obj, role, "recipient_id")

        # id of the current unit which has the staff member who has the role of the current unit
        unit_id_role = get_recipient_list(obj, role, "id")

        # name of the staff member who has the role of the current unit
        staff_name = GeStaff.objects.filter(id=staff_id_role[0]).values_list(
            "name", flat=True
        )

        # return a link to manage the unit and role of the staff member
        # who has the role of the current unit
        result = (
            "<a href=../../../admin/ge/gerecipient/"
            + str(unit_id_role[0])
            + "/change/>"
            + str(staff_name[0])
            + "</a>"
        )
        return result
    else:
        # id from the unit table of the current unit
        unit_id_num = getattr(obj, "id")

        # return a link to add a recipient (staff member) and role
        # to the current unit which currently has none
        result = (
            "<a href=../../../admin/ge/gerecipient/add/?geunit="
            + str(unit_id_num)
            + ">-----</a>"
        )
        return result


# return id given recipient type (aul, head or assoc) and column name of the value needed
def get_recipient_list(obj, recipient_type, value_needed):
    result = GeRecipient.objects.filter(
        unit_id=getattr(obj, "id"), role=recipient_type
    ).values_list(value_needed, flat=True)
    return result
