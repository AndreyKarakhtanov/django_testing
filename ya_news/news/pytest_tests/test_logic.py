# news/pytest_tests/test_logic.py
import pytest
from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

BAD_TEXT = f'Какой-то текст, {BAD_WORDS[0]}, еще текст'


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client, form_data, news_id_for_args
):
    """Тест: Анонимный пользователь не может отправить комментарий."""
    url = reverse('news:detail', args=news_id_for_args)
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
        author_client, author, form_data, news, news_id_for_args
):
    """Тест: Авторизованный пользователь может отправить комментарий."""
    url = reverse('news:detail', args=news_id_for_args)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, url + '#comments')
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.news == news
    assert new_comment.text == form_data['text']
    assert new_comment.author == author


def test_catch_bad_words(author_client, form_data, news_id_for_args):
    """Тест: Если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    url = reverse('news:detail', args=news_id_for_args)
    form_data['text'] = BAD_TEXT
    # Пытаемся создать новую заметку:
    response = author_client.post(url, data=form_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(
    author_client, form_data, comment, news, author,
    news_id_for_args, comment_id_for_args
):
    """Тест: Авторизованный пользователь может редактировать
    свои комментарии.
    """
    url = reverse('news:edit', args=comment_id_for_args)
    response = author_client.post(url, form_data)
    assertRedirects(
        response,
        reverse('news:detail', args=news_id_for_args) + '#comments'
    )
    comment.refresh_from_db()
    assert comment.news == news
    assert comment.text == form_data['text']
    assert comment.author == author


def test_author_can_delete_comment(
        author_client, comment_id_for_args,
        news_id_for_args
):
    """Тест: Авторизованный пользователь может удалять свои комментарии."""
    url = reverse('news:delete', args=comment_id_for_args)
    response = author_client.post(url)
    assertRedirects(
        response,
        reverse('news:detail', args=news_id_for_args) + '#comments'
    )
    assert Comment.objects.count() == 0


def test_other_user_cant_edit_comment(
        not_author_client, form_data, comment, comment_id_for_args
):
    """Тест: Авторизованный пользователь не может редактировать
    чужие комментарии.
    """
    url = reverse('news:edit', args=comment_id_for_args)
    response = not_author_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.news == comment_from_db.news
    assert comment.text == comment_from_db.text
    assert comment.author == comment_from_db.author


def test_other_user_cant_delete_note(not_author_client, comment_id_for_args):
    """Тест: Авторизованный пользователь не может удалять чужие комментарии."""
    url = reverse('news:delete', args=comment_id_for_args)
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
