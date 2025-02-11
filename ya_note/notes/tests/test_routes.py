from http import HTTPStatus

from django.contrib.auth import get_user_model

from .test_base import TestBase

User = get_user_model()


class TestRoutes(TestBase):
    """Тестирование маршрутов"""

    def test_pages_availability_for_users(self):
        """Тест: Главная страница, страницы регистрации пользователей,
        входа в учётную запись и выхода из неё доступны всем пользователям.
        Аутентифицированному пользователю доступна страница со списком
        заметок notes/, страница успешного добавления заметки done/, страница
        добавления новой заметки add/.
        Страницы отдельной заметки, удаления и редактирования заметки
        доступны только автору заметки. Если на эти страницы попытается зайти
        другой пользователь — вернётся ошибка 404.
        """
        urls = (
            (self.NOTES_HOME_URL, self.client, HTTPStatus.OK),
            (self.USERS_LOGIN_URL, self.client, HTTPStatus.OK),
            (self.USERS_LOGOUT_URL, self.client, HTTPStatus.OK),
            (self.USERS_SIGNUP_URL, self.client, HTTPStatus.OK),
            (self.NOTES_HOME_URL, self.author_client, HTTPStatus.OK),
            (self.USERS_LOGIN_URL, self.author_client, HTTPStatus.OK),
            (self.USERS_SIGNUP_URL, self.author_client, HTTPStatus.OK),
            (self.NOTES_LIST_URL, self.author_client, HTTPStatus.OK),
            (self.NOTES_ADD_URL, self.author_client, HTTPStatus.OK),
            (self.NOTES_SUCCESS_URL, self.author_client, HTTPStatus.OK),
            (self.NOTES_DETAIL_URL, self.author_client, HTTPStatus.OK),
            (self.NOTES_EDIT_URL, self.author_client, HTTPStatus.OK),
            (self.NOTES_DELETE_URL, self.author_client, HTTPStatus.OK),
            (self.NOTES_DETAIL_URL, self.reader_client, HTTPStatus.NOT_FOUND),
            (self.NOTES_EDIT_URL, self.reader_client, HTTPStatus.NOT_FOUND),
            (self.NOTES_DELETE_URL, self.reader_client, HTTPStatus.NOT_FOUND),
            (self.USERS_LOGOUT_URL, self.author_client, HTTPStatus.OK),
        )
        for url, parametrized_client, status in urls:
            with self.subTest(
                url=url,
                parametrized_client=parametrized_client,
                status=status
            ):
                response = parametrized_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Тест: При попытке перейти на страницу списка заметок,
        страницу успешного добавления записи, страницу добавления заметки,
        отдельной заметки, редактирования или удаления заметки
        анонимный пользователь перенаправляется на страницу логина.
        """
        urls = (
            self.NOTES_EDIT_URL,
            self.NOTES_DETAIL_URL,
            self.NOTES_DELETE_URL,
            self.NOTES_ADD_URL,
            self.NOTES_LIST_URL,
            self.NOTES_SUCCESS_URL
        )
        for url in urls:
            with self.subTest(url=url):
                redirect_url = f'{self.USERS_LOGIN_URL}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
