from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects

from django.urls import reverse


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('pk_news_for_args')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    )
)
def test_pages_availability(client, name, args):
    """Проверка доступности страниц у неавторизованного пользователя.

    Неавторизованному пользователю доступны следующие страницы:
    списка новостей, новости отдельно, авторизации, регистрации
    и выхода из учетной записи.
    """
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK, (
        'Неавторизованному пользователю недоступны страницы.'
    )


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('pk_comment_for_args')),
        ('news:delete', pytest.lazy_fixture('pk_comment_for_args'))
    )
)
def test_redirects_for_anonymous(client, name, args):
    """Проверка редиректов для неавторизованных пользователей.

    При переходе на страницы редактирвоания и изменения комментария,
    неавторизованного пользователя направляет на страницу авторизации.
    """
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(
        response,
        expected_url,
        msg_prefix='Не выполняется редирект неавторизованного клиента.'
    )


@pytest.mark.parametrize(
    'parametrized_client, expected_status, msg',
    (
        (
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK,
            'Автору недоступны страницы удаления и редактирования заметки.'
        ),
        (
            pytest.lazy_fixture('reader_client'),
            HTTPStatus.NOT_FOUND,
            'Cтраница удаления и редактирования доступна другим юзерам.'
        ),
    )
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_comment_edit_delete_for_different_users(
    parametrized_client, name, pk_comment_for_args, expected_status, msg
):
    """Проверка перехода на страницу редактирования и удаления.

    Только автор может перейти на страницу редактирования и удаления
    своего комментария, другим пользователям выпадает 404 ошибка.
    """
    url = reverse(name, args=pk_comment_for_args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status, msg
