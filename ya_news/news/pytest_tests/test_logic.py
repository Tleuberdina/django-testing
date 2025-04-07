from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError
from django.contrib.auth import get_user_model

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


User = get_user_model()


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client,
    url_detail_news,
    form_data
):
    """Проверяем, что анонимный пользователь не может отправить комментарий."""
    client.post(url_detail_news, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_can_create_comment(
    not_author,
    not_author_client,
    news,
    url_detail_news,
    form_data
):
    """
    Проверяем, что авторизованный пользователь
    может отправить комментарий.
    """
    response = not_author_client.post(url_detail_news, data=form_data)
    assertRedirects(response, f'{url_detail_news}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == not_author


@pytest.mark.django_db
@pytest.mark.parametrize(
    'bad_words',
    (BAD_WORDS),
)
def test_user_cant_use_bad_words(
    not_author_client,
    url_detail_news,
    bad_words
):
    """
    Проверяем, что если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    bad_words_data = {'text': f'Какой-то текст, {bad_words}, еще текст'}
    response = not_author_client.post(url_detail_news, data=bad_words_data)
    assertFormError(response.context['form'], 'text', WARNING)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_author_can_delete_comment(
    author_client,
    url_detail_news,
    url_delete_comment,
):
    """Проверяем, что автор может удалять свои комментарии."""
    response = author_client.delete(url_delete_comment)
    assertRedirects(response, f'{url_detail_news}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(
    not_author_client,
    url_delete_comment,
    comment
):
    """
    Проверяем, что авторизованный пользователь
    не может удалять чужие комментарии.
    """
    response = not_author_client.delete(url_delete_comment)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(
    author_client,
    url_detail_news,
    news,
    url_edit_comment,
    author,
    comment,
    form_data
):
    """Проверяем, что автор может редактировать свои комментарии."""
    response = author_client.post(url_edit_comment, data=form_data)
    assertRedirects(response, f'{url_detail_news}#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(
    not_author_client,
    url_edit_comment,
    comment,
    form_data
):
    """
    Проверяем, что авторизованный пользователь
    не может редактировать чужие комментарии.
    """
    response = not_author_client.post(url_edit_comment, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_db.text
    assert comment.news == comment_db.news
    assert comment.author == comment_db.author
