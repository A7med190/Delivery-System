from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_reference', 'order', 'user', 'amount', 'method', 'status', 'paid_at']
    list_filter = ['status', 'method', 'created_at']
    search_fields = ['payment_reference', 'order__order_number', 'user__email', 'transaction_id']
    readonly_fields = ['payment_reference', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
