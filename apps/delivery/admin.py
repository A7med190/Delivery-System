from django.contrib import admin
from .models import Delivery, DeliveryLocation


class DeliveryLocationInline(admin.TabularInline):
    model = DeliveryLocation
    extra = 0
    readonly_fields = ['latitude', 'longitude', 'accuracy', 'speed', 'recorded_at']


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['tracking_number', 'order', 'driver', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['tracking_number', 'order__order_number', 'driver__email']
    readonly_fields = ['tracking_number', 'created_at', 'updated_at']
    inlines = [DeliveryLocationInline]


@admin.register(DeliveryLocation)
class DeliveryLocationAdmin(admin.ModelAdmin):
    list_display = ['delivery', 'latitude', 'longitude', 'accuracy', 'recorded_at']
    list_filter = ['recorded_at']
