import random

import pytest
from django.urls import reverse
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_403_FORBIDDEN, HTTP_204_NO_CONTENT


# проверка получения 1го подборки
@pytest.mark.django_db
def test_collection_retrieve(collection_factory, user_api_client):
    collection = collection_factory()[0]
    url = reverse("product-collections-detail", args=[collection.id])

    resp = user_api_client.get(url)
    resp_json = resp.json()

    assert resp.status_code == HTTP_200_OK
    assert resp_json["id"] == collection.id


# проверка получения списка подборок
@pytest.mark.django_db
def test_collections_list(user_api_client, collection_factory):
    collections_list = collection_factory()
    url = reverse("product-collections-list")

    resp = user_api_client.get(url)
    resp_json = resp.json()

    assert resp.status_code == HTTP_200_OK
    assert len(resp_json) == 10


# тест на добавление подборки
# администратором
@pytest.mark.django_db
def test_collection_create_by_admin(admin_api_client, collection_create_payload):
    url = reverse("product-collections-list")

    resp = admin_api_client.post(url, data=collection_create_payload, format="json")
    resp_json = resp.json()

    assert resp.status_code == HTTP_201_CREATED
    assert resp_json["title"]== collection_create_payload["title"]
    assert resp_json["text"] == collection_create_payload["text"]
    assert resp_json["products_list"][0]["product_id"] == collection_create_payload["products_list"][0]["product_id"]


# пользователем (должен вызывать ошибку)
@pytest.mark.django_db
def test_collection_create_by_user(user_api_client, collection_create_payload):
    url = reverse("product-collections-list")

    resp = user_api_client.post(url, data=collection_create_payload, format="json")

    assert resp.status_code == HTTP_403_FORBIDDEN


# тест на обновление подборки
# администратором
@pytest.mark.django_db
def test_collections_update_by_admin(collection_factory, admin_api_client):
    collection = collection_factory(title="collection")[0]

    url = reverse("product-collections-detail", args=[collection.id])
    payload = {"title": f"test_{collection.title}"}

    resp = admin_api_client.patch(url, data=payload)
    resp_json = resp.json()

    assert resp.status_code == HTTP_200_OK
    assert payload["title"] == resp_json["title"]


# пользователем (должен вызывать ошибку)
@pytest.mark.django_db
def test_collections_update_by_user(collection_factory, user_api_client):
    collection = collection_factory(title="collection")[0]

    url = reverse("product-collections-detail", args=[collection.id])
    payload = {"title": f"test_{collection.title}"}

    resp = user_api_client.patch(url, data=payload)

    assert resp.status_code == HTTP_403_FORBIDDEN


# тест на удаление подборки
# администратором
@pytest.mark.django_db
def test_collections_delete_by_admin(collection_factory, admin_api_client):
    random_collection = random.choice(collection_factory())
    url = reverse("product-collections-detail", args=[random_collection.id])

    resp = admin_api_client.delete(url)
    existing_ids = [collection["id"] for collection in admin_api_client.get(reverse("product-collections-list")).json()]

    assert resp.status_code == HTTP_204_NO_CONTENT
    assert random_collection.id not in existing_ids


# пользователем (должен вызывать ошибку)
@pytest.mark.django_db
def test_collections_delete_by_user(collection_factory, user_api_client):
    random_collection = random.choice(collection_factory())
    url = reverse("product-collections-detail", args=[random_collection.id])

    resp = user_api_client.delete(url)

    assert resp.status_code == HTTP_403_FORBIDDEN
