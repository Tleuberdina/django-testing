from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        (pytest.lazy_fixture('url_home'), None),
        (pytest.lazy_fixture('url_detail'),
         pytest.lazy_fixture('slug_for_args')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None)
    ),
)
def test_pages_availability_for_anonymous_user(client, name, args):
    """
    Проверяем, что анонимному пользователю доступны страницы:
    главная страница, регистрации пользователей,
    входа в учетную запись, выхода из учетной записи,
    отдельной новости.
    """
    url = reverse(name, args=args)
    response = client.get(url)
    if name == 'users:logout':
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
    else:
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
    'name',
    (pytest.lazy_fixture('url_edit_comment'),
     pytest.lazy_fixture('url_delete_comment')),
)
def test_availability_for_comment_edit_and_delete(
        parametrized_client, name, comment, expected_status
):
    """
    Проверяем, что на страницы редактирования и удаления комментария
    автору доступны, а авторизированному пользователю
    недоступны(возвращается ошибка 404).
    """
    url = reverse(name, args=(comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, news_object',
    (
        (pytest.lazy_fixture('url_edit_comment'),
         pytest.lazy_fixture('comment_slug_for_args')),
        (pytest.lazy_fixture('url_delete_comment'),
         pytest.lazy_fixture('comment_slug_for_args')),
    ),
)
def test_redirects(client, name, news_object):
    """
    Проверяем, что при попытке перейти на страницу редактирования
    или удаления комментария анонимный пользователь
    перенаправляется на страницу авторизации.
    """
    login_url = reverse('users:login')
    if news_object is not None:
        url = reverse(name, args=news_object)
    else:
        url = reverse(name)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
