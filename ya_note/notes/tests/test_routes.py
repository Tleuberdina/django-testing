from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author = User.objects.create(username='Читатель простой')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='note-slug',
            author=cls.author)
        cls.url_add = reverse('notes:add', args=None)
        cls.url_success = reverse('notes:success', args=None)
        cls.url_home = reverse('notes:home', args=None)
        cls.url_detail = reverse('notes:detail', args=(cls.note.slug,))
        cls.url_edit = reverse('notes:edit', args=(cls.note.slug,))
        cls.url_delete = reverse('notes:delete', args=(cls.note.slug,))
        cls.url_list = reverse('notes:list', args=None)

    def test_pages_home_availability(self):
        """Проверяем, что анонимному пользователю доступна главная страница."""
        response = self.client.get(self.url_home)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_login_and_signup_availability(self):
        """Проверяем, что анонимному пользователю доступны страницы:
        регистрации пользователей, входа в учётную запись.
        """
        urls = (
            ('users:login', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_and_delete(self):
        """
        Проверяем, что страницы отдельной записи, редактирования записи
        и удаления записи доступна только автору заметки, другим
        пользователям при попытки зайти на данные страницы -
        вернётся ошибка 404.
        """
        users_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.not_author_client, HTTPStatus.NOT_FOUND),
        )
        urls = (
            (self.url_detail),
            (self.url_edit),
            (self.url_delete),
        )
        for user, status in users_statuses:
            for url in urls:
                with self.subTest(user=user, name=url):
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    def test_pages_availability_for_auth_user(self):
        """
        Проверяем, что аутентифицированному пользователю
        доступны страницы: со списком заметок, успешного
        добавления заметки, добавления новой заметки.
        """
        urls = (
            (self.url_list),
            (self.url_success),
            (self.url_add),
        )
        for url in urls:
            with self.subTest(name=url):
                response = self.not_author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        """Проверяем, что при попытке перейти на страницы: списка заметок,
        успешного добавления записи, добавления заметки, отдельной заметки,
        редактирования или удаления заметки анонимный пользователь
        перенаправляется на страницу логина.
        """
        urls = (
            (self.url_list),
            (self.url_edit),
            (self.url_delete),
            (self.url_success),
            (self.url_add),
            (self.url_detail),
        )
        login_url = reverse('users:login')
        for url in urls:
            with self.subTest(name=url):
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
