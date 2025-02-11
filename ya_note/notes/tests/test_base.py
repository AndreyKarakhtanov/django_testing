from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note


User = get_user_model()


class TestBase(TestCase):
    """Базовый класс тестирования."""
    NOTES_HOME_URL = reverse('notes:home')
    USERS_LOGIN_URL = reverse('users:login')
    USERS_LOGOUT_URL = reverse('users:logout')
    USERS_SIGNUP_URL = reverse('users:signup')
    NOTES_LIST_URL = reverse('notes:list')
    NOTES_ADD_URL = reverse('notes:add')
    NOTES_SUCCESS_URL = reverse('notes:success')
    NOTE_TITLE = 'Тестовая заметка'
    NOTE_TEXT = 'Просто текст.'
    NOTE_SLUG = slugify(NOTE_TITLE)
    NEW_NOTE_TITLE = 'Супер заметка'
    NEW_NOTE_TEXT = 'Супер текст.'
    NEW_NOTE_SLUG = slugify(NEW_NOTE_TITLE)
    NOTES_DETAIL_URL = reverse('notes:detail', args=(NOTE_SLUG,))
    NOTES_EDIT_URL = reverse('notes:edit', args=(NOTE_SLUG,))
    NOTES_DELETE_URL = reverse('notes:delete', args=(NOTE_SLUG,))

    @classmethod
    def setUpTestData(cls):
        """Подготовка базовых фиксур."""
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.author
        )
