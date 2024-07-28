from http import HTTPStatus

from django.urls import reverse

from .common_data import BaseTestCase


class TestRoutes(BaseTestCase):
    """Класс проверки отображения соответсвующих страницы."""

    URLS_FOR_NOT_AUTH = (
        'notes:home',
        'users:login',
        'users:logout',
        'users:signup',
    )
    URLS_FOR_AUTH = (
        'notes:add',
        'notes:list',
        'notes:success',
    )

    def test_pages_availability(self):
        """Проверка доступности страниц у неавторизованного пользователя.

        Неавторизованному пользователю доступны следующие страницы:
        главная, авторизации, регистрации и выхода из учетной записи.
        """
        for name in self.URLS_FOR_NOT_AUTH:
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
                self.author_client,
                HTTPStatus.OK,
                'Автору недоступны страницы удаления и редактирования заметки.'
            ),
            (
                self.not_author_client,
                HTTPStatus.NOT_FOUND,
                'Cтраница удаления и редактирования доступна другим юзерам.'
            )
        )
        for user, status, msg in user_statuses:
            for name in ('notes:detail', 'notes:edit', 'notes:delete'):
                with self.subTest(user=user, status=status):
                    url = reverse(name, kwargs={'slug': self.note.slug})
                    response = user.get(url)
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
        for name in self.URLS_FOR_AUTH + self.URLS_FOR_NOT_AUTH:
            url = reverse(name)
            response = self.author_client.get(url)
            self.assertEqual(
                response.status_code,
                HTTPStatus.OK,
                msg='Основные страницы недоступны для пользователей сайта.'
            )
