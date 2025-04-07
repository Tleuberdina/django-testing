from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'urls',
    (
        (pytest.lazy_fixture('url_home')),
        (pytest.lazy_fixture('url_detail_news')),
    ),
)
def test_pages_detail_and_home_availability_for_anonymous_user(client, urls):
    """
    Проверяем, что анонимному пользователю доступны страницы:
    главная страница, отдельной новости.
    """
    response = client.get(urls)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('users:login', None),
        ('users:signup', None)
    ),
)
def test_pages_login_and_signup_availability_for_anonymous_user(
    client,
    name,
    args
):
    """
    Проверяем, что анонимному пользователю доступны страницы:
    регистрации пользователей, входа в учетную запись.
    """
    url = reverse(name, args=args)
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
    'urls',
    (pytest.lazy_fixture('url_edit_comment'),
     pytest.lazy_fixture('url_delete_comment')),
)
def test_availability_for_comment_edit_and_delete(
        parametrized_client, urls, comment, expected_status
):
    """
    Проверяем, что на страницы редактирования и удаления комментария
    автору доступны, а авторизированному пользователю
    недоступны(возвращается ошибка 404).
    """
    response = parametrized_client.get(urls)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'urls',
    (
        (pytest.lazy_fixture('url_edit_comment')),
        (pytest.lazy_fixture('url_delete_comment')),
    ),
)
def test_redirects(client, urls):
    """
    Проверяем, что при попытке перейти на страницу редактирования
    или удаления комментария анонимный пользователь
    перенаправляется на страницу авторизации.
    """
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={urls}'
    response = client.get(urls)
    assertRedirects(response, expected_url)
