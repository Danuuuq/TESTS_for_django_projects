import pytest

from django.conf import settings
from django.urls import reverse


def test_news_count_and_order(client, news_list):
    """Проверка кол-ва новостей на главной странице и их сортировка.

    На главной странице должна быть пагинация по кол-ву указанному
    в настройках, сортировка по дате от новой к старой.
    """
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert (
        news_count == settings.NEWS_COUNT_ON_HOME_PAGE
        and all_dates == sorted_dates
    ), 'На странице больше новостей или они неправильно отсортированы'


@pytest.mark.parametrize(
    'parametrized_client, form_in_list, msg',
    (
        (
            pytest.lazy_fixture('author_client'),
            True,
            'Авторизованному пользователю недоступна форма для комментария.'
        ),
        (
            pytest.lazy_fixture('client'),
            False,
            'Неавторизованному пользователю доступна форма для заметки.'
        ),
    )
)
def test_pages_contains_form(
    parametrized_client, pk_news_for_args, form_in_list, msg
):
    """Проверка наличия формы для комментария.

    Форма должна быть доступна только автроизованному пользователю.
    """
    url = reverse('news:detail', args=pk_news_for_args)
    response = parametrized_client.get(url)
    assert ('form' in response.context) is form_in_list, msg


def test_comment_order(client, comment_list, pk_news_for_args):
    """Проверка сортировка комментариев.

    Комментарии должны быть отсортированы от старых к новым.
    """
    url = reverse('news:detail', args=pk_news_for_args)
    response = client.get(url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_dates = [comment.created for comment in all_comments]
    sorted_dates = sorted(all_dates)
    assert all_dates == sorted_dates, 'Комментарии отсортированы некорректно'
