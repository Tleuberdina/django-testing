from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url',
    (
        (pytest.lazy_fixture('url_home')),
        (pytest.lazy_fixture('url_detail_news')),
        (pytest.lazy_fixture('url_login')),
        (pytest.lazy_fixture('url_signup')),
    ),
)
def test_pages_availability_for_anonymous_user(client, url):
    """
    Проверяем, что анонимному пользователю доступны страницы:
    главная страница, отдельной новости.
    """
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'url',
    (pytest.lazy_fixture('url_edit_comment'),
     pytest.lazy_fixture('url_delete_comment')),
)
def test_availability_for_comment_edit_and_delete(
        parametrized_client, url, comment, expected_status
):
    """
    Проверяем, что на страницы редактирования и удаления комментария
    автору доступны, а авторизированному пользователю
    недоступны(возвращается ошибка 404).
    """
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url',
    (
        (pytest.lazy_fixture('url_edit_comment')),
        (pytest.lazy_fixture('url_delete_comment')),
    ),
)
def test_redirects(client, url, url_login):
    """
    Проверяем, что при попытке перейти на страницу редактирования
    или удаления комментария анонимный пользователь
    перенаправляется на страницу авторизации.
    """
    expected_url = f'{url_login}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
