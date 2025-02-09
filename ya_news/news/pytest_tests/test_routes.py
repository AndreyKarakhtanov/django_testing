# news/pytest_tests/test_routes.py
from http import HTTPStatus
import pytest

from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news_id_for_args')),
        ('users:signup', None),
        ('users:login', None),
        ('users:logout', None),
    ),
)
def test_pages_availability_for_anonymous_user(client, name, args):
    """Тест: Главная страница, страница отдельной новости,
    страницы регистрации пользователей, входа в учётную запись
    и выхода из неё доступны анонимным пользователям.
    """
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_pages_availability_for_different_users(
        parametrized_client, name, comment_id_for_args, expected_status
):
    """Тест: Страницы удаления и редактирования комментария
    доступны автору комментария и
    недоступны другим авторизованым пользователям.
    """
    url = reverse(name, args=comment_id_for_args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    (
        'news:edit', 'news:delete'
    )
)
def test_redirects(client, name, comment_id_for_args):
    """Тест: При попытке перейти на страницу редактирования или
    удаления комментария анонимный пользователь перенаправляется
    на страницу авторизации.
    """
    login_url = reverse('users:login')
    url = reverse(name, args=comment_id_for_args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
