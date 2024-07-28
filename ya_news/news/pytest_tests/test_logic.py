from http import HTTPStatus
import pytest
from pytest_django.asserts import assertFormError

from django.urls import reverse
from django.test.client import Client

from news.models import Comment
from news.forms import WARNING


@pytest.mark.parametrize(
    'parametrized_client, comment_in_list, msg',
    (
        (
            pytest.lazy_fixture('author_client'),
            True,
            'Авторизованный пользователь не смог написать комментарий!'
        ),
        (
            Client(),
            False,
            'Неавторизованный пользователь смог написать комментария!'
        ),
    )
)
def test_sent_comment_client_and_anonymous(
    parametrized_client, comment_in_list,
    msg, form_comment, pk_news_for_args, delete_comments
):
    """Проверка возможности отправки комментариев.

    Неавторизованный пользователь не должен иметь возможности
    отправлять комментарии.
    """
    url = reverse('news:detail', args=pk_news_for_args)
    Comment.objects.all().delete()
    parametrized_client.post(url, form_comment)
    assert Comment.objects.count() == comment_in_list, msg


@pytest.mark.parametrize(
    'parametrized_client, comment_in_list, status_page, msg',
    (
        (
            pytest.lazy_fixture('author_client'),
            False,
            HTTPStatus.FOUND,
            'Автор не смог удалить свой комментарий!'
        ),
        (
            pytest.lazy_fixture('reader_client'),
            True,
            HTTPStatus.NOT_FOUND,
            'Пользователь смог удалить чужой комментарий!'
        ),
    )
)
def test_delete_comment_diferent_user(
    parametrized_client, comment_in_list, status_page,
    pk_comment_for_args, msg, comment
):
    """Проверка возможности удаления комментария.

    Удалить комментария может только его автор.
    """
    url = reverse('news:delete', args=pk_comment_for_args)
    assert Comment.objects.count() == 1, (
        'В базе данных создаются ещё комментарии, должен быть один.'
    )
    response = parametrized_client.post(url)
    assert response.status_code == status_page
    assert Comment.objects.count() == comment_in_list, msg


def test_edit_comment_author(
    author_client, pk_comment_for_args, form_comment, comment
):
    """Проверка возможности редактирования комментария автором.

    Редактировать комментария может только его автор.
    """
    url = reverse('news:edit', args=pk_comment_for_args)
    response = author_client.post(url, form_comment)
    assert response.status_code == HTTPStatus.FOUND
    comment_from_db = Comment.objects.get(pk=comment.pk)
    assert comment_from_db.text == form_comment['text'], (
        'Автор не смог отредактировать свой комментарий!'
    )


def test_edit_comment_not_author(
    reader_client, pk_comment_for_args, form_comment, comment
):
    """Проверка возможности редактирования чужих комментариев.

    Пользователи не могут редактировать чужие коментарии.
    """
    url = reverse('news:edit', args=pk_comment_for_args)
    response = reader_client.post(url, form_comment)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(pk=comment.pk)
    assert comment_from_db.text == comment.text, (
        'Пользователь смог отредактировать чужой комментарий!'
    )


def test_bad_word_in_comment(
    author_client, bad_form_comment, pk_news_for_args, delete_comments
):
    """Проверка возможности использования недопустимых слов.

    Пользователи не могут использовать в комментариях недопустимые слова,
    которые указаны в forms.py d списке bad_form.
    """
    url = reverse('news:detail', args=pk_news_for_args)
    response = author_client.post(url, data=bad_form_comment)
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.count() == 0, (
        'Пользователь смог написать недопустимое слово в комментарии'
    )
