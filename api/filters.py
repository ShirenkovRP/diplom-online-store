from django_filters import rest_framework as filters

from .models import Product, ProductReview, Order, Collection


class ProductFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='contains')
    description = filters.CharFilter(field_name='description', lookup_expr='contains')
    price = filters.RangeFilter(field_name='price')

    class Meta:
        model = Product
        fields = ('name', 'description', 'price',)


class ProductReviewFilter(filters.FilterSet):
    user = 'user__id'
    positions = filters.NumberFilter(field_name='product__id')
    created_at = filters.DateFromToRangeFilter(field_name='created_at')

    class Meta:
        model = ProductReview
        fields = ('user', 'product', 'created_at')


class OrderFilter(filters.FilterSet):
    created_at = filters.DateFromToRangeFilter(field_name='created_at')
    updated_at = filters.DateFromToRangeFilter(field_name='created_at')
    order_sum = filters.RangeFilter(field_name='order_sum')
    product_id = filters.NumberFilter(field_name='positions__product_id')

    class Meta:
        model = Order
        fields = ('status', 'order_sum', 'updated_at', 'created_at')


class CollectionFilter(filters.FilterSet):
    class Meta:
        model = Collection
        fields = []
