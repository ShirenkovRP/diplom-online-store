import random

import pytest
from django.urls import reverse
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_403_FORBIDDEN, HTTP_204_NO_CONTENT


# проверка получения 1го отзыва
@pytest.mark.django_db
def test_review_retrieve(user_api_client, review_factory):
    review = review_factory()[0]
    url = reverse("product-reviews-detail", args=[review.id])

    resp = user_api_client.get(url)
    resp_json = resp.json()

    assert resp.status_code == HTTP_200_OK
    assert resp_json["id"] == review.id


# проверка получения списка отзыва
@pytest.mark.django_db
def test_reviews_list(user_api_client, review_factory):
    reviews_list = review_factory()
    url = reverse("product-reviews-list")

    resp = user_api_client.get(url)
    resp_json = resp.json()

    assert resp.status_code == HTTP_200_OK
    assert len(resp_json) == 10


# проверка фильтрации списка отзывов по user_id
@pytest.mark.django_db
def test_reviews_filter_by_user_id(user_api_client, review_factory):
    random_review_user_id = random.choice(review_factory()).user_id
    url = reverse("product-reviews-list")

    resp = user_api_client.get(url, {"user": random_review_user_id})
    resp_json = resp.json()[0]

    assert resp.status_code == HTTP_200_OK
    assert resp_json["user"] == random_review_user_id


# проверка фильтрации списка отзывов по дате создания
@pytest.mark.django_db
def test_reviews_filter_by_creation_date(user_api_client, review_factory):
    random_review_creation_date = random.choice(review_factory()).created_at
    url = reverse("product-reviews-list")

    resp = user_api_client.get(url, {"created_at": random_review_creation_date})
    resp_json = resp.json()[0]

    assert resp.status_code == HTTP_200_OK
    assert resp_json["created_at"] == str(random_review_creation_date)


# проверка фильтрации списка отзывов по продукту
@pytest.mark.django_db
def test_reviews_filter_by_product_id(user_api_client, review_factory):
    random_review_product_id = random.choice(review_factory()).product.id
    url = reverse("product-reviews-list")

    resp = user_api_client.get(url, {"product": random_review_product_id})
    resp_json = resp.json()[0]

    assert resp.status_code == HTTP_200_OK
    assert resp_json["product"] == random_review_product_id


# Тест на добавление отзыва
# администратором
@pytest.mark.django_db
def test_review_update_by_admin(review_factory, admin_api_client):
    review = review_factory()[0]

    url = reverse("product-reviews-detail", args=[review.id])
    payload = {"text": f"test_{review.text}"}

    resp = admin_api_client.patch(url, data=payload)
    resp_json = resp.json()

    assert resp.status_code == HTTP_200_OK
    assert resp_json["text"] == payload["text"]


# пользователем
@pytest.mark.django_db
def test_reviews_create(user_api_client, review_create_payload):
    url = reverse("product-reviews-list")

    resp = user_api_client.post(url, data=review_create_payload, format="json")
    resp_json = resp.json()

    assert resp.status_code == HTTP_201_CREATED
    assert resp_json["product"] == review_create_payload["product"] and resp_json["text"] == review_create_payload[
        "text"] and resp_json["rating"] == review_create_payload["rating"]


# Тест на обновление отзыва
# пользователем
@pytest.mark.django_db
def test_review_update_by_owner(review_factory, user_api_client, user):
    review = review_factory()[0]
    review.user = user

    url = reverse("product-reviews-detail", args=[review.id])
    payload = {"text": f"test_{review.text}"}

    resp = user_api_client.patch(url, data=payload)
    resp_json = resp.json()

    assert resp.status_code == HTTP_200_OK
    assert resp_json["text"] == payload["text"]


# не авторизованным пользователем (должен вызвать ошибку)
@pytest.mark.django_db
def test_review_update_by_another_user(review_factory, another_user_api_client, user):
    review = review_factory()[0]
    review.user = user

    url = reverse("product-reviews-detail", args=[review.id])
    payload = {"text": f"test_{review.text}"}

    resp = another_user_api_client.patch(url, data=payload)

    assert resp.status_code == HTTP_403_FORBIDDEN


# Тест на удаление отзыва
# администратором
@pytest.mark.django_db
def test_review_delete_by_admin(review_factory, admin_api_client):
    random_review = random.choice(review_factory())

    url = reverse("product-reviews-detail", args=[random_review.id])

    resp = admin_api_client.delete(url)
    existing_ids = [product["id"] for product in admin_api_client.get(reverse("product-reviews-list")).json()]

    assert resp.status_code == HTTP_204_NO_CONTENT
    assert random_review.id not in existing_ids


# пользователем
@pytest.mark.django_db
def test_review_delete_by_owner(review_factory, user_api_client, user):
    random_review = random.choice(review_factory())
    random_review.user = user

    url = reverse("product-reviews-detail", args=[random_review.id])

    resp = user_api_client.delete(url)
    existing_ids = [product["id"] for product in user_api_client.get(reverse("product-reviews-list")).json()]

    assert resp.status_code == HTTP_204_NO_CONTENT
    assert random_review.id not in existing_ids


# не авторизованным пользователем (должен вызвать ошибку)
@pytest.mark.django_db
def test_review_delete_by_another_user(review_factory, another_user_api_client, user):
    random_review = random.choice(review_factory())
    random_review.user = user

    url = reverse("product-reviews-detail", args=[random_review.id])

    resp = another_user_api_client.delete(url)

    assert resp.status_code == HTTP_403_FORBIDDEN
