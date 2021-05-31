from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ProductViewSet, ProductReviewViewSet, OrderViewSet, CollectionViewSet, FavoritesViewSet

router = DefaultRouter()
router.register('products', ProductViewSet, 'products')
router.register('product-reviews', ProductReviewViewSet, 'product-reviews')
router.register('orders', OrderViewSet, 'orders')
router.register('collections', CollectionViewSet, 'product-collections')
router.register('favorites', FavoritesViewSet, 'favorites')

urlpatterns = [
    path('', include(router.urls)),
]
