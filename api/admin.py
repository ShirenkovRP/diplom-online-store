from django.contrib import admin
from .models import ProductCollection, ProductOrder, Product, ProductReview, Order, Collection


class ProductCollectionInline(admin.TabularInline):
    model = ProductCollection


class ProductOrderInline(admin.TabularInline):
    model = ProductOrder


# Товар
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    pass


# Отзыв к товару
@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    pass


# Заказы
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [ProductOrderInline]


# Подборки
@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    inlines = [ProductCollectionInline]
