from django.contrib import admin
from .models import Address


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'address_type', 'label', 'street_address', 'city', 'is_default']
    list_filter = ['address_type', 'is_default', 'city']
    search_fields = ['user__email', 'street_address', 'city', 'postal_code']
    ordering = ['-created_at']
