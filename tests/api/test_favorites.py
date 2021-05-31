import random

import pytest
from django.urls import reverse
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_201_CREATED, HTTP_204_NO_CONTENT


# проверка получения 1го избранного
@pytest.mark.django_db
def test_favorites_retrieve_by_owner(favorites_factory, user_api_client, user):
    favorites = favorites_factory()[0]
    url = reverse('favorites-detail', args=[favorites.id])

    resp = user_api_client.get(url)
    resp_json = resp.json()

    assert resp.status_code == HTTP_200_OK
    assert resp_json['id'] == favorites.id


# проверка получения 1го избранного
# другим пользователем (должна вызывать ошибку)
@pytest.mark.django_db
def test_favorites_retrieve_by_another_user(favorites_factory, another_user_api_client, user):
    favorites = favorites_factory()[0]
    url = reverse('favorites-detail', args=[favorites.id])

    resp = another_user_api_client.get(url)

    assert resp.status_code == HTTP_404_NOT_FOUND


# проверка получения списка избранного
@pytest.mark.django_db
def test_favorites_list(favorites_factory, user_api_client):
    favorites_list = favorites_factory()
    url = reverse('favorites-list')

    resp = user_api_client.get(url)
    resp_json = resp.json()

    assert resp.status_code == HTTP_200_OK
    assert len(resp_json) == 10


# тест на добавление в избранное
@pytest.mark.django_db
def test_favorites_create(favorites_factory, user_api_client, favorites_create_payload):
    url = reverse('favorites-list')

    resp = user_api_client.post(url, data=favorites_create_payload, format='json')
    resp_json = resp.json()

    assert resp.status_code == HTTP_201_CREATED
    assert resp_json['product'] == favorites_create_payload['product']


# тест на удаление из избранного
# пользователем
@pytest.mark.django_db
def test_favorites_delete(favorites_factory, user_api_client):
    random_fav = random.choice(favorites_factory())
    url = reverse('favorites-detail', args=[random_fav.id])

    resp = user_api_client.delete(url)
    existing_ids = [product['id'] for product in user_api_client.get(reverse('favorites-list')).json()]

    assert resp.status_code == HTTP_204_NO_CONTENT
    assert random_fav.id not in existing_ids

# не авторизованным пользователем (должна вызывать ошибку)
@pytest.mark.django_db
def test_favorites_delete_by_another_user(favorites_factory, another_user_api_client):
    random_fav = random.choice(favorites_factory())
    url = reverse('favorites-detail', args=[random_fav.id])

    resp = another_user_api_client.delete(url)

    assert resp.status_code == HTTP_404_NOT_FOUND
