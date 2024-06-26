from django.contrib import admin
from .models import Category, Product, Customer, Order, OrderItem, Supplier, Stock, Review

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock')
    list_filter = ('category',)
    search_fields = ('name',)

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'address')
    search_fields = ('user__username', 'phone')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer', 'created_at', 'is_paid')
    list_filter = ('is_paid', 'created_at')
    search_fields = ('customer__user__username',)
    inlines = [OrderItemInline]

class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_name', 'phone', 'email')
    search_fields = ('name', 'contact_name')

class StockAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'updated_at')
    list_filter = ('updated_at',)
    search_fields = ('product__name',)

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'customer', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'customer__user__username')

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Supplier, SupplierAdmin)
admin.site.register(Stock, StockAdmin)
admin.site.register(Review, ReviewAdmin)
