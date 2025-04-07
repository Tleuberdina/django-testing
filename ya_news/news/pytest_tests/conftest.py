from datetime import datetime, timedelta

import pytest
from django.test.client import Client
from django.utils import timezone
from django.conf import settings
from django.urls import reverse

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def url_login():
    return reverse('users:login')


@pytest.fixture
def url_signup():
    return reverse('users:signup')


@pytest.fixture
def url_home():
    return reverse('news:home')


@pytest.fixture
def url_detail_news(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def url_detail_comment(comment):
    return reverse('news:detail', args=(comment.id,))


@pytest.fixture
def url_delete_comment(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def url_edit_comment(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def news():
    return News.objects.create(
        title='Новость',
        text='Текст новости',
    )


@pytest.fixture
def all_news(news):
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст',
    }


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news,
        text='Текст комментария',
        author=author
    )


@pytest.fixture
def new_comment(news, author):
    now = timezone.now()
    for index in range(10):
        new_comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        new_comment.created = now + timedelta(days=index)
