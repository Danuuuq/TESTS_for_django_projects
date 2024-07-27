from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestNotePage(TestCase):
    """Класс проверки корректной работы с контентом."""

    ADD_NOTE_PAGE = reverse('notes:add')
    NOTES_PAGE = reverse('notes:list')

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
            title='Заметка', text='Текст', author=cls.author
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_note_list_for_diferent_users(self):
        """Проверка страницы со всеми заметками пользователя.

        В списке заметок, должны быть видно только собственные заметки.
        """
        user_note = (
            (
                self.author_client,
                True,
                'У Автора не отображаются собственные заметки.'
            ),
            (
                self.not_author_client,
                False,
                'У пользователей отображаются чужие заметки.'
            )
        )
        for user, note_in_list, msg in user_note:
            with self.subTest(user=user, note_in_list=note_in_list, msg=msg):
                response = user.get(self.NOTES_PAGE)
                object_list = response.context['object_list']
                self.assertEqual(
                    (self.note in object_list),
                    note_in_list,
                    msg=msg
                )

    def test_authorized_has_form_add(self):
        """Проверка наличия формы у авторизованного пользователя.

        При переходе на страницу создания заметки проверяется,
        что авторизованный пользователь получает форму для заметки.
        """
        response = self.author_client.get(self.ADD_NOTE_PAGE)
        self.assertIn('form', response.context)
        self.assertIsInstance(
            response.context['form'],
            NoteForm,
            msg='Авторизованному пользователю недоступна форма для заметки.'
        )

    def test_authorized_has_form_edit(self):
        """Проверка наличия формы у неавторизованного пользователя.

        При переходе на страницу создания заметки проверяется,
        что неавторизованный пользователь не получает форму для заметки.
        """
        response = self.author_client.get(self.edit_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(
            response.context['form'],
            NoteForm,
            'Неавторизованному пользователю доступна форма для заметки.'
        )
