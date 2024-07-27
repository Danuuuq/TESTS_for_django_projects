from http import HTTPStatus

from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    """Класс проверки создания новых заметок."""

    NOTE_TITLE = 'Название заметки'
    NOTE_TEXT = 'Текст заметки'
    NOTE_SLUG = 'just_slug'
    URL_ADD = reverse('notes:add')

    @classmethod
    def setUpTestData(cls):
        """Создание объектов для тестирования."""
        cls.user = User.objects.create(username='Автор')
        cls.auth_user = Client()
        cls.auth_user.force_login(cls.user)
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': cls.NOTE_SLUG
        }

    def test_create_note_anonymous_and_user(self):
        """Проверка возможности создания заметки.

        Только авторизованный пользователь может создавать заметки.
        """
        user_note = (
            (
                self.client,
                False,
                'Неавторизованный пользователь смог создать заметку!'
            ),
            (
                self.auth_user,
                True,
                'Авторизованны пользователь не смог создать заметку!'
            )
        )
        for user, note_in_list, msg in user_note:
            with self.subTest(user=user, note_in_list=note_in_list, msg=msg):
                user.post(self.URL_ADD, data=self.form_data)
                notes_count = Note.objects.count()
                self.assertEqual(notes_count, note_in_list, msg=msg)

    def test_create_note_with_empty_slug(self):
        """Проверка транслитерации названия заметки в slug.

        Если при создании не указано поле slug оно формируется из название.
        """
        form_data = self.form_data
        form_data.pop('slug')
        self.auth_user.post(self.URL_ADD, data=form_data)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(
            new_note.slug,
            expected_slug,
            msg='Транслитерация работает некорректно.'
        )


class TestNoteEditDelete(TestCase):
    """Класс проверки редактирования и удаления заметки."""

    NOTE_TITLE = 'Название заметки'
    NOTE_TEXT = 'Текст заметки'
    NEW_TITLE = 'Обновленное название заметки'
    NEW_TEXT = 'Обновленный текст заметки'
    NOTE_SLUG = 'just_slug'
    URL_ADD = reverse('notes:add')

    @classmethod
    def setUpTestData(cls):
        """Подготовка объектов для тестирования."""
        cls.author = User.objects.create(username='Автор публикации')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Автор без публикации')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.author,
            slug=cls.NOTE_SLUG
        )
        cls.url_to_success = reverse('notes:success')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {'title': cls.NEW_TITLE, 'text': cls.NEW_TEXT}

    def test_unique_slug(self):
        """Проверка невозможности создания неуникального slug.

        Пользователь не может создать заметку у которой slug не уникальный.
        """
        not_unique_slug = {'slug': self.NOTE_SLUG}
        response = self.author_client.post(self.URL_ADD, data=not_unique_slug)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=self.NOTE_SLUG + WARNING
        )
        notes_count = Note.objects.count()
        self.assertEqual(
            notes_count,
            1,
            msg='Пользователь может создать неуникальный slug!'
        )

    def test_author_can_delete_note(self):
        """Проверка возможности удаления заметки автором."""
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.url_to_success)
        notes_count = Note.objects.count()
        self.assertEqual(
            notes_count,
            0,
            msg='Автор не смог удалить свою заметку!'
        )

    def test_user_cant_delete_another_note(self):
        """Проверка невозможности удаления чужих заметок."""
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(
            notes_count,
            1,
            msg='Пользователь смог удалить чужую заметку!'
        )

    def test_author_can_edit_note(self):
        """Проверка возможности редактироваия заметки автором."""
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.url_to_success)
        self.note.refresh_from_db()
        self.assertEqual(
            (self.note.title, self.note.text),
            (self.NEW_TITLE, self.NEW_TEXT),
            msg='Автор не смог отредактировать свою заметку!'
        )

    def test_user_cant_edit_another_note(self):
        """Проверка невозможности редактирования чужих заметок."""
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(
            (self.note.title, self.note.text),
            (self.NOTE_TITLE, self.NOTE_TEXT),
            msg='Пользователь смог отредактировать чужую заметку!'
        )
