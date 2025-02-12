from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


BAD_TEXT = f'Какой-то текст, {BAD_WORDS[0]}, еще текст'


def test_anonymous_user_cant_create_comment(
        client, form_data, news_detail_url, users_login_url
):
    """Тест: Анонимный пользователь не может отправить комментарий."""
    response = client.post(news_detail_url, data=form_data)
    expected_url = f'{users_login_url}?next={news_detail_url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
        author_client, author, form_data, news, news_detail_url
):
    """Тест: Авторизованный пользователь может отправить комментарий."""
    response = author_client.post(news_detail_url, data=form_data)
    assertRedirects(response, news_detail_url + '#comments')
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.news == news
    assert new_comment.text == form_data['text']
    assert new_comment.author == author


def test_catch_bad_words(author_client, form_data, news_detail_url):
    """Тест: Если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    form_data['text'] = BAD_TEXT
    # Пытаемся создать новую заметку:
    response = author_client.post(news_detail_url, data=form_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(
        author_client, form_data, comment, news, author,
        news_edit_url, news_detail_url
):
    """Тест: Авторизованный пользователь может редактировать
    свои комментарии.
    """
    response = author_client.post(news_edit_url, form_data)
    assertRedirects(response, news_detail_url + '#comments')
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.news == comment.news
    assert comment_from_db.text == form_data['text']
    assert comment_from_db.author == comment.author


def test_author_can_delete_comment(
        author_client, news_delete_url, news_detail_url
):
    """Тест: Авторизованный пользователь может удалять свои комментарии."""
    response = author_client.post(news_delete_url)
    assertRedirects(response, news_detail_url + '#comments')
    assert Comment.objects.count() == 0


def test_other_user_cant_edit_comment(
        not_author_client, form_data, comment, news_edit_url
):
    """Тест: Авторизованный пользователь не может редактировать
    чужие комментарии.
    """
    response = not_author_client.post(news_edit_url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.news == comment_from_db.news
    assert comment.text == comment_from_db.text
    assert comment.author == comment_from_db.author


def test_other_user_cant_delete_note(not_author_client, news_delete_url):
    """Тест: Авторизованный пользователь не может удалять чужие комментарии."""
    response = not_author_client.post(news_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
