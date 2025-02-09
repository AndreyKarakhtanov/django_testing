# notes/tests/test_content.py
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestDetailPage(TestCase):
    """Тестирование контента"""
    @classmethod
    def setUpTestData(cls):
        """Подготовка фиксур"""
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        all_notes = [
            Note(
                title=f'Заметка {index}',
                text='Просто текст.',
                slug=f'zametka_{index}',
                author=cls.author
            )
            for index in range(20)
        ]
        Note.objects.bulk_create(all_notes)
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Просто текст.',
            author=cls.author
        )
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.list_url = reverse('notes:list')
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_notes_order(self):
        self.client.force_login(self.author)
        response = self.client.get(self.list_url)
        self.assertIn('object_list', response.context)
        # Получаем объект новости.
        notes = response.context['object_list']
        all_notes_id = [note.id for note in notes]
        sorted_notes_id = sorted(all_notes_id)
        self.assertEqual(all_notes_id, sorted_notes_id)

    def test_notes_list_for_different_users(self):
        """Тест: отдельная заметка передаётся на страницу со списком заметок
        в списке object_list в словаре contextв и список заметок
        одного пользователя не попадают заметки другого пользователя.
        """
        users_values = (
            (self.author, True),
            (self.reader, False),
        )
        for user, value in users_values:
            self.client.force_login(user)
            with self.subTest(user=user):
                response = self.client.get(self.list_url)
                object_list = response.context['object_list']
                self.assertEqual(self.note in object_list, value)

    def test_authorized_client_has_form(self):
        """Тест: на страницы создания и редактирования заметки
        передаются формы.
        """
        self.client.force_login(self.author)
        responses = [
            self.client.get(self.add_url),
            self.client.get(self.edit_url),
        ]
        for response in responses:
            with self.subTest():
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
