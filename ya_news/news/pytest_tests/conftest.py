# news/pytest_tests/conftest.py
import pytest
from datetime import datetime, timedelta

from django.conf import settings
from django.test.client import Client
from django.utils import timezone

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    """Фикстура для пользователя автор"""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    """Фикстура для другого пользователя"""
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    """Фикстура для авторизации автора"""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    """Фикстура для авторизации другого пользователя"""
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    """Фикстура для создания новости"""
    news = News.objects.create(
        title='Заголовок',
        text='Текст комментария'
    )
    return news


@pytest.fixture
def news_set():
    """Фикстура для создания набора новостей"""
    today = datetime.today()
    news_set = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            # Для каждой новости уменьшаем дату на index дней от today,
            # где index - счётчик цикла.
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(news_set)


@pytest.fixture
def news_id_for_args(news):
    """Фикстура возвращает id новости в кортеже"""
    return (news.id,)


@pytest.fixture
def comment(news, author):
    """Фикстура для создания коментария от автора"""
    comment = Comment.objects.create(
        news=news,
        text='Текст комментария',
        author=author,
    )
    return comment


@pytest.fixture
def comments_set(author, news):
    """Фикстура для создания набора комментариев"""
    now = timezone.now()
    # Создаём комментарии в цикле.
    for index in range(10):
        # Создаём объект и записываем его в переменную.
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        # Сразу после создания меняем время создания комментария.
        comment.created = now + timedelta(days=index)
        # И сохраняем эти изменения.
        comment.save()


@pytest.fixture
def comment_id_for_args(comment):
    """Фикстура возвращает id коментария в кортеже"""
    return (comment.id,)


@pytest.fixture
def form_data(author, news):
    """Фикстура формы для новости"""
    return {
        'news': news,
        'text': 'Новый комментарий',
        'author': author
    }
