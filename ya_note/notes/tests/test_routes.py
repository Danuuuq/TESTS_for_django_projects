from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    """Класс проверки отображения соответсвующих страницы."""

    @classmethod
    def setUpTestData(cls):
        """Создание объектов для тестирования."""
        cls.author_1 = User.objects.create(username='Тестовый полюзователь 1')
        cls.author_2 = User.objects.create(username='Тестовый пользователь 2')
        cls.note = Note.objects.create(
            title='Название',
            text='Текст заметки',
            author=cls.author_1
        )

    def test_pages_availability(self):
        """Проверка доступности страниц у неавторизованного пользователя.

        Неавторизованному пользователю доступны следующие страницы:
        главная, авторизации, регистрации и выхода из учетной записи.
        """
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    msg='Неавторизованному пользователю недоступны страницы.'
                )

    def test_availability_for_note_edit_and_delete(self):
        """Проверка редактирования и удаления заметки.

        Редактирование и удаление заметок доступно только автору заметки
        не автору заметки возвращается ошибка 404.
        """
        user_statuses = (
            (
                self.author_1,
                HTTPStatus.OK,
                'Автору недоступны страницы удаления и редактирования заметки.'
            ),
            (
                self.author_2,
                HTTPStatus.NOT_FOUND,
                'Cтраница удаления и редактирования доступна другим юзерам.'
            )
        )
        for user, status, msg in user_statuses:
            self.client.force_login(user)
            for name in ('notes:detail', 'notes:edit', 'notes:delete'):
                with self.subTest(user=user, status=status):
                    url = reverse(name, kwargs={'slug': self.note.slug})
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status, msg=msg)

    def test_redirect_for_anonymous_client(self):
        """Проверка редиректов для неавторизованных пользователей.

        При переходе на страницы работы с заметками, неавторизованного
        пользователя направляет на страницу авторизации.
        """
        login_url = reverse('users:login')
        urls = (
            ('notes:add', None),
            ('notes:detail', (self.note.slug, )),
            ('notes:edit', (self.note.slug, )),
            ('notes:delete', (self.note.slug, )),
            ('notes:list', None),
            ('notes:success', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(
                    response,
                    redirect_url,
                    msg_prefix=(
                        'Не выполняется редирект неавторизованного клиента.'
                    )
                )

    def test_availability_for_client(self):
        """Проверка страниц для авторизованных пользовтаелей.

        Страницы всех заметок и их создания, авторизации, регистрации
        и выхода из учетной записи доступны всем.
        """
        urls = (
            'notes:add',
            'notes:list',
            'notes:success',
            'users:login',
            'users:logout',
            'users:signup',
        )
        user = self.author_1
        self.client.force_login(user)
        for name in urls:
            url = reverse(name)
            response = self.client.get(url)
            self.assertEqual(
                response.status_code,
                HTTPStatus.OK,
                msg='Основные страницы недоступны для пользователей сайта.'
            )
