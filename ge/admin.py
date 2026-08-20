from django.contrib import admin
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
    list_display = ["name"]
    ordering = ("name",)
    search_fields = ["name"]


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
    ordering = (
        "unit__name",
        "role",
    )
    search_fields = ["recipient__name", "unit__name", "role"]

    @admin.display(description="Name", ordering="recipient__name")
    def get_name(self, recipient):
        return recipient.recipient.name

    @admin.display(description="Unit", ordering="unit__name")
    def get_unit(self, recipient):
        return recipient.unit.name
