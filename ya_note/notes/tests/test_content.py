from notes.forms import NoteForm
from .common_data import BaseTestCase


class TestNotePage(BaseTestCase):
    """Класс проверки корректной работы с контентом."""

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
                response = user.get(self.URL_NOTES_PAGE)
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
        response = self.author_client.get(self.URL_ADD_NOTE_PAGE)
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
        response = self.author_client.get(self.url_edit)
        self.assertIn('form', response.context)
        self.assertIsInstance(
            response.context['form'],
            NoteForm,
            'Неавторизованному пользователю доступна форма для заметки.'
        )
