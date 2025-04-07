import pytest
from django.conf import settings

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(client, url_home, all_news):
    """Проверяем количество новостей на главной странице."""
    response = client.get(url_home)
    assert 'object_list' in response.context
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, url_home):
    """Проверяем сортировку новостей от самой свежей к самой старой."""
    response = client.get(url_home)
    assert 'object_list' in response.context
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, url_detail_comment, new_comment):
    """На отдельной странице новости проверяем сортировку
    комментариев от старой к новой.
    """
    response = client.get(url_detail_comment)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, url_detail_comment):
    """
    Проверяем, что анонимному пользователю недоступна
    форма для отправки комментария на отдельной странице новости.
    """
    response = client.get(url_detail_comment)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(author_client, url_detail_comment):
    """
    Проверяем, что авторизованному пользователю доступна
    форма для отправки комментария на отдельной странице новости.
    """
    response = author_client.get(url_detail_comment)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
