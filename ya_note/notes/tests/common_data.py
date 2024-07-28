from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class BaseTestCase(TestCase):
    """Базовый класс для тестов."""

    NOTE_TITLE = 'Название заметки'
    NOTE_TEXT = 'Текст заметки'
    NOTE_SLUG = 'just_slug'
    NOTE_NEW_TITLE = 'Обновленное название заметки'
    NOTE_NEW_TEXT = 'Обновленный текст заметки'
    URL_ADD = reverse('notes:add')
    URL_ADD_NOTE_PAGE = reverse('notes:add')
    URL_NOTES_PAGE = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        """Создание объектов для тестирования."""
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author = User.objects.create(username='Не автор')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.author,
            slug=cls.NOTE_SLUG
        )
        cls.form_data = {
            'title': cls.NOTE_NEW_TITLE,
            'text': cls.NOTE_NEW_TEXT,
            'slug': cls.NOTE_SLUG
        }
        cls.url_to_success = reverse('notes:success')
        cls.url_edit = reverse('notes:edit', args=(cls.note.slug,))
        cls.url_delete = reverse('notes:delete', args=(cls.note.slug,))
