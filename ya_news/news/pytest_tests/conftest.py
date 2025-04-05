import pytest
from datetime import datetime, timedelta

from django.test.client import Client
from django.utils import timezone
from django.conf import settings

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
def news():
    news = News.objects.create(
        title='Новость',
        text='Текст новости',
    )
    return news


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
    return all_news


@pytest.fixture
def slug_for_args(news):
    return (news.id,)


@pytest.fixture
def form_data():
    return {
        'title': 'Новый заголовок',
        'text': 'Новый текст',
    }


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        text='Текст комментария',
        author=author
    )
    return comment


@pytest.fixture
def two_comment(news, author):
    now = timezone.now()
    for index in range(10):
        two_comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        two_comment.created = now + timedelta(days=index)
    return


@pytest.fixture
def comment_slug_for_args(comment):
    return (comment.id,)
