from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


NEWS_HOME_URL = pytest.lazy_fixture('news_home_url')
USERS_LOGIN_URL = pytest.lazy_fixture('users_login_url')
USERS_SIGNUP_URL = pytest.lazy_fixture('users_signup_url')
USERS_LOGOUT_URL = pytest.lazy_fixture('users_logout_url')
NEWS_DETAIL_URL = pytest.lazy_fixture('news_detail_url')
NEWS_EDIT_URL = pytest.lazy_fixture('news_edit_url')
NEWS_DELETE_URL = pytest.lazy_fixture('news_delete_url')
CLIENT = pytest.lazy_fixture('client')
AUTHOR_CLIENT = pytest.lazy_fixture('author_client')
NOT_AUTHOR_CLIENT = pytest.lazy_fixture('not_author_client')


@pytest.mark.parametrize(
    'url, parametrized_client, status',
    (
        (NEWS_HOME_URL, CLIENT, HTTPStatus.OK),
        (NEWS_DETAIL_URL, CLIENT, HTTPStatus.OK),
        (USERS_SIGNUP_URL, CLIENT, HTTPStatus.OK),
        (USERS_LOGIN_URL, CLIENT, HTTPStatus.OK),
        (USERS_LOGOUT_URL, CLIENT, HTTPStatus.OK),
        (NEWS_HOME_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (NEWS_DETAIL_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (USERS_SIGNUP_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (USERS_LOGIN_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (USERS_LOGOUT_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (NEWS_EDIT_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (NEWS_DELETE_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (NEWS_EDIT_URL, NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
        (NEWS_DELETE_URL, NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND)
    )
)
def test_pages_availability_for_users(parametrized_client, url, status):
    """Тест: Главная страница, страница отдельной новости,
    страницы регистрации пользователей, входа в учётную запись
    и выхода из неё доступны всем пользователям.
    Страницы удаления и редактирования комментария доступны автору комментария
    и недоступны другим даже авторизованым пользователям.
    """
    response = parametrized_client.get(url)
    assert response.status_code == status


@pytest.mark.parametrize(
    'url',
    (
        NEWS_EDIT_URL,
        NEWS_DELETE_URL
    ),
)
def test_redirects(client, url, users_login_url):
    """Тест: При попытке перейти на страницу редактирования или
    удаления комментария анонимный пользователь перенаправляется
    на страницу авторизации.
    """
    expected_url = f'{users_login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
