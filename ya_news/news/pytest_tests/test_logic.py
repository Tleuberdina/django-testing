import pytest
from pytest_django.asserts import assertRedirects

from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse

from news.forms import CommentForm, BAD_WORDS, WARNING
from news.models import Comment


User = get_user_model()


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment1(client, news, form_data):
    url = reverse('news:detail', args=(news.id,))
    client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_can_create_comment1(
    not_author,
    not_author_client,
    news,
    form_data
):
    url = reverse('news:detail', args=(news.id,))
    response = not_author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == 'Новый текст'
    assert comment.news == news
    assert comment.author == not_author


@pytest.mark.django_db
def test_user_cant_use_bad_words1():
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    form = CommentForm(data=bad_words_data)
    assert 'text' in form.errors
    assert form.errors['text'] == [WARNING]
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_author_can_delete_comment1(author_client, news, comment):
    delete_url = reverse('news:delete', args=(comment.id,))
    response = author_client.delete(delete_url)
    url = reverse('news:detail', args=(news.id,))
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(not_author_client, comment):
    delete_url = reverse('news:delete', args=(comment.id,))
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment1(author_client, news, comment, form_data):
    edit_url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(edit_url, data=form_data)
    url = reverse('news:detail', args=(news.id,))
    assertRedirects(response, f'{url}#comments')
    comment.refresh_from_db()
    assert comment.text == 'Новый текст'


def test_user_cant_edit_comment_of_another_user1(
    not_author_client,
    comment,
    form_data
):
    edit_url = reverse('news:edit', args=(comment.id,))
    response = not_author_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == 'Текст комментария'
