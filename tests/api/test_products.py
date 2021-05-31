import random

import pytest
from django.urls import reverse
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_403_FORBIDDEN, HTTP_204_NO_CONTENT


# проверка получения 1го продукта (retrieve-логика)
@pytest.mark.django_db
def test_product_retrieve(user_api_client, product_factory):
    product = product_factory()[0]
    url = reverse("products-detail", args=[product.id])

    resp = user_api_client.get(url)
    resp_json = resp.json()

    assert resp.status_code == HTTP_200_OK
    assert product.id == resp_json["id"]


# проверка получения списка продуктов (list-логика)
@pytest.mark.django_db
def test_products_list(user_api_client, product_factory):
    products_list = product_factory()
    url = reverse("products-list")

    resp = user_api_client.get(url)
    resp_json = resp.json()

    assert resp.status_code == HTTP_200_OK
    assert len(resp_json) == 10


# проверка фильтрации списка по цене
@pytest.mark.django_db
def test_products_filter_by_price(user_api_client, product_factory):
    random_product_price = random.choice(product_factory()).price
    url = reverse("products-list")

    resp = user_api_client.get(url, {"price_min": random_product_price, "price_max": random_product_price})
    resp_json = resp.json()[0]

    assert resp.status_code == HTTP_200_OK
    assert resp_json["price"] == random_product_price


# проверка фильтрации списка по наименованию продукта
@pytest.mark.django_db
def test_products_filter_by_name(user_api_client, product_factory):
    random_product_name = random.choice(product_factory()).name
    url = reverse("products-list")

    resp = user_api_client.get(url, {"name": random_product_name})
    resp_json = resp.json()[0]

    assert resp.status_code == HTTP_200_OK
    assert resp_json["name"] == random_product_name


# проверка фильтрации списка по описанию продукта
@pytest.mark.django_db
def test_products_filter_by_description(user_api_client, product_factory):
    random_product_description = random.choice(product_factory()).description
    url = reverse("products-list")

    resp = user_api_client.get(url, {"description": random_product_description})
    resp_json = resp.json()[0]

    assert resp.status_code == HTTP_200_OK
    assert resp_json["description"] == random_product_description


# Тест на добавление продукта
# Проверка на добавление продукта администратором
@pytest.mark.django_db
def test_products_create_by_admin(product_factory, admin_api_client, product_create_payload):
    url = reverse("products-list")

    resp = admin_api_client.post(url, data=product_create_payload, format="json")
    resp_json = resp.json()

    assert resp.status_code == HTTP_201_CREATED
    assert resp_json["name"] == product_create_payload["name"]


# Проверка на добавление продукта пользователем (должна вызывать ошибку)
@pytest.mark.django_db
def test_products_create_by_user(product_factory, user_api_client, product_create_payload):
    url = reverse("products-list")

    resp = user_api_client.post(url, data=product_create_payload, format="json")

    assert resp.status_code == HTTP_403_FORBIDDEN


# Тест на изменение продукта
# Проверка на изменение имени продукта администратором
@pytest.mark.django_db
def test_products_update_by_admin(product_factory, admin_api_client):
    product = product_factory(name="product")[0]

    url = reverse("products-detail", args=[product.id])
    payload = {"name": f"test_{product.name}"}

    resp = admin_api_client.patch(url, data=payload)
    resp_json = resp.json()

    assert resp.status_code == HTTP_200_OK
    assert payload["name"] == resp_json["name"]


# Проверка на изменение имени продукта пользователем (должна вызывать ошибку)
@pytest.mark.django_db
def test_products_update_by_user(product_factory, user_api_client):
    product = product_factory(name="product")[0]

    url = reverse("products-detail", args=[product.id])
    payload = {"name": f"test_{product.name}"}

    resp = user_api_client.patch(url, data=payload)

    assert resp.status_code == HTTP_403_FORBIDDEN


# Тест на удаление продукта
# Проверка на удаление продукта администратором
@pytest.mark.django_db
def test_products_delete_by_admin(product_factory, admin_api_client):
    random_product = random.choice(product_factory())
    url = reverse("products-detail", args=[random_product.id])

    resp = admin_api_client.delete(url)
    existing_ids = [product["id"] for product in admin_api_client.get(reverse("products-list")).json()]

    assert resp.status_code == HTTP_204_NO_CONTENT
    assert random_product.id not in existing_ids


# Проверка на удаление продукта пользователем (должна вызывать ошибку)
@pytest.mark.django_db
def test_products_delete_by_user(product_factory, user_api_client):
    random_product = random.choice(product_factory())
    url = reverse("products-detail", args=[random_product.id])

    resp = user_api_client.delete(url)

    assert resp.status_code == HTTP_403_FORBIDDEN
