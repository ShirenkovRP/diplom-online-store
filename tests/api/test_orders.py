import random

import pytest
from django.urls import reverse
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT
from api.models import OrderStatusChoices


# проверка получения 1го заказ
@pytest.mark.django_db
def test_order_retrieve(order_factory, user_api_client):
    order = order_factory()[0]
    url = reverse("orders-detail", args=[order.id])

    resp = user_api_client.get(url)
    resp_json = resp.json()

    assert resp.status_code == HTTP_200_OK
    assert resp_json["id"] == order.id


# проверка получения списка заказов
@pytest.mark.django_db
def test_order_list(order_factory, user_api_client):
    orders_list = order_factory()
    url = reverse("orders-list")

    resp = user_api_client.get(url)
    resp_json = resp.json()

    assert resp.status_code == HTTP_200_OK
    assert len(resp_json) == 10


# проверка фильтрации по статусу заказа
@pytest.mark.django_db
def test_order_filter_by_status(order_factory, admin_api_client):
    orders_list = order_factory()
    random_status = random.choices(OrderStatusChoices.names)[0]
    url = reverse("orders-list")

    resp = admin_api_client.get(url, {"status": random_status})
    resp_json = resp.json()
    expected_ids = {order.id for order in orders_list if order.status == random_status}
    resp_ids = {order.get("id") for order in resp_json}

    assert resp.status_code == HTTP_200_OK
    assert expected_ids == resp_ids


# проверка фильтрации по сумме заказа
@pytest.mark.django_db
def test_order_filter_by_order_sum(order_factory, admin_api_client):
    random_order_sum = random.choices(order_factory())[0].order_sum
    url = reverse("orders-list")

    resp = admin_api_client.get(url, {"order_sum_min": random_order_sum, "order_sum_max": random_order_sum})
    resp_json = resp.json()[0]

    assert resp.status_code == HTTP_200_OK
    assert resp_json["order_sum"] == random_order_sum


# проверка фильтрации по дате создания заказа
@pytest.mark.django_db
def test_order_filter_by_creation_date(order_factory, admin_api_client):
    random_order_creation_date = random.choice(order_factory()).created_at
    url = reverse("orders-list")

    resp = admin_api_client.get(url, {"created_at": random_order_creation_date})
    resp_json = resp.json()[0]

    assert resp.status_code == HTTP_200_OK
    assert resp_json["created_at"] == str(random_order_creation_date)


# проверка фильтрации по обновлению заказа
@pytest.mark.django_db
def test_order_filter_by_update_date(order_factory, admin_api_client):
    random_order_update_date = random.choice(order_factory()).created_at
    url = reverse("orders-list")

    resp = admin_api_client.get(url, {"created_at": random_order_update_date})
    resp_json = resp.json()[0]

    assert resp.status_code == HTTP_200_OK
    assert resp_json["created_at"] == str(random_order_update_date)


# проверка проверка фильтрации заказа по продукту
@pytest.mark.django_db
def test_order_filter_by_product(order_factory, admin_api_client):
    random_order = random.choice(order_factory())
    random_product = random.choice(random_order.products.all())
    url = reverse("orders-list")

    resp = admin_api_client.get(url, {"product_id": random_product.id})
    resp_json = resp.json()[0]

    assert resp.status_code == HTTP_200_OK
    assert resp_json["id"] == random_order.id


# тест на добавление заказа
@pytest.mark.django_db
def test_order_create(user_api_client, order_create_payload):
    url = reverse("orders-list")
    product_id = order_create_payload["positions"][0]["product_id"]
    amount = order_create_payload["positions"][0]["amount"]

    resp = user_api_client.post(url, data=order_create_payload, format="json")
    assert resp.status_code == HTTP_201_CREATED

    resp_json = resp.json()
    assert resp_json["positions"][0]["product_id"] == product_id and resp_json["positions"][0]["amount"] == amount


# тест на обновление заказа
# администратором
@pytest.mark.django_db
def test_order_update_by_admin(admin_api_client, order_update_payload):
    url, payload = order_update_payload
    product_id = payload["positions"][0]["product_id"]
    amount = payload["positions"][0]["amount"]

    resp = admin_api_client.patch(url, data=payload, format="json")
    resp_json = resp.json()


    assert resp.status_code == HTTP_200_OK
    assert resp_json["positions"][0]["product_id"] == product_id and resp_json["positions"][0]["amount"] == amount


# пользователем
@pytest.mark.django_db
def test_order_update_by_owner(user_api_client, order_update_payload):
    url, payload = order_update_payload
    product_id = payload["positions"][0]["product_id"]
    amount = payload["positions"][0]["amount"]

    resp = user_api_client.patch(url, data=payload, format="json")
    resp_json = resp.json()

    assert resp.status_code == HTTP_200_OK
    assert resp_json["positions"][0]["product_id"] == product_id and resp_json["positions"][0]["amount"] == amount


# не авторизованным пользователем (должен вызывать ошибку)
@pytest.mark.django_db
def test_order_update_by_another_user(another_user_api_client, order_update_payload):
    url, payload = order_update_payload

    resp = another_user_api_client.patch(url, data=payload, format="json")
    assert resp.status_code == HTTP_404_NOT_FOUND


# тест на удаление заказа
# администратором
@pytest.mark.django_db
def test_order_delete_by_admin(order_factory, admin_api_client):
    random_order = random.choices(order_factory())[0]
    url = reverse("orders-detail", args=[random_order.id])

    resp = admin_api_client.delete(url)
    existing_ids = [order["id"] for order in admin_api_client.get(reverse("orders-list")).json()]

    assert resp.status_code == HTTP_204_NO_CONTENT
    assert random_order.id not in existing_ids


# пользователем
@pytest.mark.django_db
def test_order_delete_by_owner(user_api_client, order_factory):
    random_order = random.choices(order_factory())[0]
    url = reverse("orders-detail", args=[random_order.id])

    resp = user_api_client.delete(url)
    existing_ids = [order["id"] for order in user_api_client.get(reverse("orders-list")).json()]

    assert resp.status_code == HTTP_204_NO_CONTENT
    assert random_order.id not in existing_ids


# не авторизованным пользователем (должен вызывать ошибку)
@pytest.mark.django_db
def test_order_delete_by_another_user(another_user_api_client, order_factory):
    random_order = random.choices(order_factory())[0]
    url = reverse("orders-detail", args=[random_order.id])

    resp = another_user_api_client.delete(url)

    assert resp.status_code == HTTP_404_NOT_FOUND

