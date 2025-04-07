from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestContent(TestCase):
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
        cls.url_list = reverse('notes:list', args=None)
        cls.url_edit = reverse('notes:edit', args=(cls.note.slug,))
        cls.url_add = reverse('notes:add', args=None)

    def test_notes_list_for_different_users(self):
        """
        Проверяем, что отдельная заметка передаётся на страницу
        со списком заметок и что, в список заметок одного
        пользователя не попадают заметки другого пользователя.
        """
        users_result = (
            (self.author_client, True),
            (self.not_author_client, False),
        )
        for user, result in users_result:
            response = user.get(self.url_list)
            object_list = response.context['object_list']
            assert (self.note in object_list) is result

    def test_pages_contains_form(self):
        """
        Проверяем, что на страницы создания и редактирования
        заметки передаются формы.
        """
        urls = (
            (self.url_edit),
            (self.url_add),
        )
        for url in urls:
            with self.subTest(name=url):
                response = self.author_client.get(url)
                assert 'form' in response.context
                assert isinstance(response.context['form'], NoteForm)
