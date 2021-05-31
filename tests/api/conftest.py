import pytest
from django.urls import reverse
from model_bakery import baker


# Фикстуры для тестов эндпоинта products:
@pytest.fixture
def product_factory():
    def factory(**kwargs):
        return baker.make("Product", _quantity=10, **kwargs)

    return factory


@pytest.fixture
def product_create_payload():
    return {
        "name": "test",
        "description": "test",
        "price": 100
    }


# Фикстуры для тестов эндпоинта product-reviews:
@pytest.fixture
def review_factory(user, product_factory):
    def factory(**kwargs):
        return baker.make("ProductReview", user=user, _quantity=10, **kwargs)

    return factory


@pytest.fixture
def review_create_payload(product_factory):
    product = product_factory()[0]
    return {
        "product": product.id,
        "text": "test",
        "rating": 5
    }


# Фикстуры для тестов эндпоинта orders:
@pytest.fixture
def order_factory(user):
    def factory(**kwargs):
        return baker.make("Order", user=user, _quantity=10, **kwargs, make_m2m=True)

    return factory


@pytest.fixture
def order_create_payload(product_factory):
    product = product_factory()[0]
    return {"positions": [
        {"product_id": product.id, "amount": 1}
    ]
    }


@pytest.fixture
def order_update_payload(order_factory):
    order = order_factory()[0]
    url = reverse("orders-detail", args=[order.id])

    product_id = order.positions.first().product_id
    payload = {
        "positions": [
            {
                "product_id": product_id,
                "amount": 5
            }
        ]
    }
    return url, payload


# Фикстуры для тестов эндпоинта collections:
@pytest.fixture
def collection_factory(user):
    def factory(**kwargs):
        return baker.make("Collection", _quantity=10, **kwargs, make_m2m=True)

    return factory


@pytest.fixture
def collection_create_payload(product_factory):
    product = product_factory()[0]

    return {
        "title": "test_collection",
        "text": "test",
        "products_list": [
            {
                "product_id": product.id
            },

        ]
    }


# Фикстуры для тестов эндпоинта favorites:
@pytest.fixture
def favorites_factory(user):
    def factory(**kwargs):
        return baker.make("Favorites", _quantity=10, make_m2m=True, user=user, **kwargs)

    return factory


@pytest.fixture
def favorites_create_payload(product_factory):
    product = product_factory()[0]
    return {
        "product": product.id
    }

