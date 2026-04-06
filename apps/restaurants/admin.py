from django.contrib import admin
from .models import Category, Restaurant, MenuItem, MenuCategory


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1


class MenuCategoryInline(admin.TabularInline):
    model = MenuCategory
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'category', 'status', 'is_active', 'rating']
    list_filter = ['status', 'is_active', 'category']
    search_fields = ['name', 'address', 'owner__email']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [MenuCategoryInline, MenuItemInline]


@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'restaurant', 'order', 'is_active']
    list_filter = ['is_active']


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'restaurant', 'price', 'is_available', 'is_featured']
    list_filter = ['is_available', 'is_featured', 'restaurant']
    search_fields = ['name', 'restaurant__name']
