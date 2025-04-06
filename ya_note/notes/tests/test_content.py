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
        cls.url_list = 'notes:list'
        cls.url_edit = 'notes:edit'
        cls.url_add = 'notes:add'

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
        url = reverse(self.url_list)
        for user, result in users_result:
            response = user.get(url)
            object_list = response.context['object_list']
            assert (self.note in object_list) is result

    def test_pages_contains_form(self):
        """
        Проверяем, что на страницы создания и редактирования
        заметки передаются формы.
        """
        urls = (
            (self.url_edit, (self.note.slug,)),
            (self.url_add, None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                assert 'form' in response.context
                assert isinstance(response.context['form'], NoteForm)
