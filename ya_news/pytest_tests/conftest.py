from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import News, Comment


@pytest.fixture(autouse=True)
def enable_db_access(db):
    pass


@pytest.fixture
def author(django_user_model):
    """Фикстура для пользователя автор."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    """Фикстура для другого пользователя."""
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    """Фикстура для авторизации автора."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    """Фикстура для авторизации другого пользователя."""
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    """Фикстура для создания новости."""
    return News.objects.create(
        title='Заголовок',
        text='Текст комментария'
    )


@pytest.fixture
def news_set():
    """Фикстура для создания набора новостей."""
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
def comment(news, author):
    """Фикстура для создания коментария от автора."""
    return Comment.objects.create(
        news=news,
        text='Текст комментария',
        author=author,
    )


@pytest.fixture
def comments_set(author, news):
    """Фикстура для создания набора комментариев."""
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
def form_data(author, news):
    """Фикстура формы для новости."""
    return {
        'news': news,
        'text': 'Новый комментарий',
        'author': author
    }


@pytest.fixture
def users_login_url():
    """Фикстура для получения url входа в учётную запись."""
    return reverse('users:login')


@pytest.fixture
def users_signup_url():
    """Фикстура для получения url регистрации."""
    return reverse('users:signup')


@pytest.fixture
def users_logout_url():
    """Фикстура для получения url выхода из учётной записи."""
    return reverse('users:logout')


@pytest.fixture
def news_home_url():
    """Фикстура для получения url домашней страницы."""
    return reverse('news:home')


@pytest.fixture
def news_detail_url(news):
    """Фикстура для получения url отдельной новости."""
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def news_edit_url(comment):
    """Фикстура для получения url изменения комментария."""
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def news_delete_url(comment):
    """Фикстура для получения url удаления комментария."""
    return reverse('news:delete', args=(comment.id,))
