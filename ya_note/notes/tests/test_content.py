from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestContent(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.not_author = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='note-slug',
            author=cls.author)

    def test_notes_list_for_different_users(self):
        users_result = (
            (self.author, True),
            (self.not_author, False),
        )
        url = reverse('notes:list')
        for user, result in users_result:
            self.client.force_login(user)
            response = self.client.get(url)
            object_list = response.context['object_list']
            assert (self.note in object_list) is result

    def test_pages_contains_form(self):
        self.client.force_login(self.author)
        urls = (
            ('notes:edit', (self.note.slug,)),
            ('notes:add', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                assert 'form' in response.context
                assert isinstance(response.context['form'], NoteForm)
