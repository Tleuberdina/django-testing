from pytils.translit import slugify
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client, TestCase

from notes.models import Note
from notes.forms import WARNING


User = get_user_model()


class TestCreateLogic(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author = User.objects.create(username='Читатель простой')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }
        cls.url_add = 'notes:add'
        cls.url_success = 'notes:success'

    def test_user_can_create_note(self):
        """Проверяем, что залогиненный пользователь может создать заметку."""
        Note.objects.all().delete()
        url = reverse(self.url_add)
        response = self.author_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse(self.url_success))
        self.assertEqual(Note.objects.count(), 1)
        self.new_note = Note.objects.get()
        self.assertEqual(self.new_note.title, self.form_data['title'])
        self.assertEqual(self.new_note.text, self.form_data['text'])
        self.assertEqual(self.new_note.slug, self.form_data['slug'])
        self.assertEqual(self.new_note.author, self.author)

    def anymous_user_cant_create_note(self):
        """Проверяем, что анонимный пользователь не может создать заметку."""
        note_count_db = Note.objects.count()
        url = reverse(self.url_add)
        response = self.client.post(url, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), note_count_db)

    def test_empty_slug(self):
        """
        Проверяем, что если при создании заметки не заполнен slug,
        то он формируется автоматически.
        """
        note_count_db = Note.objects.count()
        Note.objects.all().delete()
        url = reverse(self.url_add)
        self.form_data.pop('slug')
        response = self.author_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse(self.url_success))
        self.assertEqual(Note.objects.count(), (note_count_db + 1))
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestEditDeleteLogic(TestCase):
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
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }
        cls.url_edit = 'notes:edit'
        cls.url_add = 'notes:add'
        cls.url_delete = 'notes:delete'

    def test_not_unique_slug(self):
        """Проверяем, что невозможно создать две заметки с одинаковым slug."""
        note_count_db = Note.objects.count()
        url = reverse(self.url_add)
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(url, data=self.form_data)
        self.assertFormError(
            response.context['form'],
            'slug',
            (self.note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), note_count_db)

    def test_other_user_cant_edit_note(self):
        """Проверяем, что пользователь не может редактировать чужие заметки."""
        url = reverse(self.url_edit, args=(self.note.slug,))
        response = self.not_author_client.post(url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        """Проверяем, что пользователь может удалять свои заметки."""
        note_count_db = Note.objects.count()
        url = reverse(self.url_delete, args=(self.note.slug,))
        response = self.author_client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), (note_count_db - 1))

    def test_author_can_edit_note(self):
        """Проверяем, что пользователь может редактировать свои заметки."""
        url = reverse(self.url_edit, args=(self.note.slug,))
        response = self.author_client.post(url, self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_other_user_cant_delete_note(self):
        """Проверяем, что пользователь не может удалять чужие заметки."""
        note_count_db = Note.objects.count()
        url = reverse(self.url_delete, args=(self.note.slug,))
        response = self.not_author_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), note_count_db)
