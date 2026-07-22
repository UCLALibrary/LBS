from django.utils.html import mark_safe
from .models import GeStaff, GeUnit, GeFund

# Register your models here.
# create page to display GE staff
@admin.register(GeStaff)
class GeStaffAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')
    ordering = ('name',)
    search_fields = ('name', 'email')


# create page to display GE units
@admin.register(GeUnit)
class GeUnitAdmin(admin.ModelAdmin):
    list_display = ['name']
    ordering = ('name',)
    search_fields = ['name']


# create page to display GE funds
@admin.register(GeFund)
class GeFundAdmin(admin.ModelAdmin):
    list_display = ('account', 'cost_center', 'fund', 'title', 'manager', 'mtf_authority', 'fund_purpose', 'fund_summary', 'fund_restriction', 'general_notes', 'lbs_notes')
    ordering = ('account',)
    search_fields = ('account', 'fund', 'title')


