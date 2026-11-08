from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Building, Apartment, MonthlyPayment, MaintenanceTicket

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations Copropriété / Syndic', {'fields': ('role', 'phone', 'cin')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Informations Copropriété / Syndic', {'fields': ('role', 'phone', 'cin')}),
    )
    list_display = ('username', 'first_name', 'last_name', 'email', 'role', 'phone', 'cin', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'cin', 'phone')

@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'address', 'manager', 'total_units', 'created_at')
    list_filter = ('city', 'manager')
    search_fields = ('name', 'address', 'city')

@admin.register(Apartment)
class ApartmentAdmin(admin.ModelAdmin):
    list_display = ('building', 'number', 'floor', 'owner', 'tantiemes', 'opening_balance')
    list_filter = ('building__city', 'building')
    search_fields = ('number', 'owner__username', 'owner__first_name', 'owner__last_name', 'building__name')

@admin.register(MonthlyPayment)
class MonthlyPaymentAdmin(admin.ModelAdmin):
    list_display = ('apartment', 'month_name', 'amount', 'status', 'payment_date', 'updated_at')
    list_filter = ('status', 'month_name')
    search_fields = ('apartment__number', 'apartment__building__name', 'apartment__owner__username')

@admin.register(MaintenanceTicket)
class MaintenanceTicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'building', 'apartment', 'resident', 'status', 'created_at')
    list_filter = ('status', 'building')
    search_fields = ('title', 'description', 'resident__username')
