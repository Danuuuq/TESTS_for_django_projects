from http import HTTPStatus

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from .common_data import BaseTestCase


class TestNoteCreation(BaseTestCase):
    """Класс проверки создания новых заметок."""

    @classmethod
    def setUpTestData(cls):
        """Переопределение родительского класса с удалением заметки."""
        super().setUpTestData()
        cls.note.delete()

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
                self.author_client,
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
        self.author_client.post(self.URL_ADD, data=form_data)
        new_note = Note.objects.last()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(
            new_note.slug,
            expected_slug,
            msg='Транслитерация работает некорректно.'
        )


class TestNoteEditDelete(BaseTestCase):
    """Класс проверки редактирования и удаления заметки."""

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
        response = self.author_client.delete(self.url_delete)
        self.assertRedirects(response, self.url_to_success)
        notes_count = Note.objects.count()
        self.assertEqual(
            notes_count,
            False,
            msg='Автор не смог удалить свою заметку!'
        )

    def test_user_cant_delete_another_note(self):
        """Проверка невозможности удаления чужих заметок."""
        response = self.not_author_client.delete(self.url_delete)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(
            notes_count,
            True,
            msg='Пользователь смог удалить чужую заметку!'
        )

    def test_author_can_edit_note(self):
        """Проверка возможности редактироваия заметки автором."""
        response = self.author_client.post(self.url_edit, data=self.form_data)
        self.assertRedirects(response, self.url_to_success)
        self.note.refresh_from_db()
        self.assertEqual(
            (self.note.title, self.note.text),
            (self.NOTE_NEW_TITLE, self.NOTE_NEW_TEXT),
            msg='Автор не смог отредактировать свою заметку!'
        )

    def test_user_cant_edit_another_note(self):
        """Проверка невозможности редактирования чужих заметок."""
        response = self.not_author_client.post(
            self.url_edit,
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(
            (self.note.title, self.note.text),
            (self.NOTE_TITLE, self.NOTE_TEXT),
            msg='Пользователь смог отредактировать чужую заметку!'
        )
