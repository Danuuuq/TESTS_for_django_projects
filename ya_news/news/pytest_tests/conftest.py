from datetime import datetime, timedelta
import pytest

from django.conf import settings
from django.test.client import Client
from django.utils import timezone

from news.models import News, Comment
from news.forms import BAD_WORDS


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст'
    )
    return news


@pytest.fixture
def pk_news_for_args(news):
    return (news.pk, )


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def pk_comment_for_args(comment):
    return (comment.pk, )


@pytest.fixture
def news_list():
    today = datetime.today()
    news = News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Текст для теста',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )
    return news


@pytest.fixture
def comment_list(news, author):
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст {index}'
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    return comment


@pytest.fixture
def form_comment():
    return {
        'text': 'Текст измененного комментария'
    }


@pytest.fixture
def bad_form_comment():
    return {
        'text': f'Комментарий содержит: {BAD_WORDS[0]} - плохое слово'
    }


@pytest.fixture
def delete_comments():
    Comment.objects.all().delete()


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


def pytest_make_parametrize_id(val):
    return repr(val)
