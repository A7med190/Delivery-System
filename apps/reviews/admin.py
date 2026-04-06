from django.contrib import admin
from .models import Review, ReviewImage, ReviewReply


class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 1


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['customer', 'restaurant', 'rating', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'created_at', 'restaurant']
    search_fields = ['customer__email', 'restaurant__name', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ReviewImageInline]

    actions = ['approve_reviews', 'disapprove_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
    approve_reviews.short_description = 'Approve selected reviews'

    def disapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)
    disapprove_reviews.short_description = 'Disapprove selected reviews'


@admin.register(ReviewReply)
class ReviewReplyAdmin(admin.ModelAdmin):
    list_display = ['review', 'restaurant', 'created_at']
    list_filter = ['created_at']
