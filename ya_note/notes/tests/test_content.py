from django.contrib.auth import get_user_model

from notes.forms import NoteForm
from notes.models import Note

from .test_base import TestBase


User = get_user_model()


class TestDetailPage(TestBase):
    """Тестирование контента"""
    @classmethod
    def setUpTestData(cls):
        """Подготовка фиксур"""
        super(TestDetailPage, cls).setUpTestData()
        all_notes = [
            Note(
                title=f'Заметка {index}',
                text='Просто текст.',
                slug=f'zametka-{index}',
                author=cls.author
            )
            for index in range(20)
        ]
        Note.objects.bulk_create(all_notes)

    def test_notes_order(self):
        response = self.author_client.get(self.NOTES_LIST_URL)
        self.assertIn('object_list', response.context)
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
            (self.author_client, True),
            (self.reader_client, False),
        )
        for user, value in users_values:
            with self.subTest(user=user):
                response = user.get(self.NOTES_LIST_URL)
                self.assertIn('object_list', response.context)
                object_list = response.context['object_list']
                self.assertIs(self.note in object_list, value)

    def test_authorized_client_has_form(self):
        """Тест: на страницы создания и редактирования заметки
        передаются формы.
        """
        responses = [
            self.author_client.get(self.NOTES_ADD_URL),
            self.author_client.get(self.NOTES_EDIT_URL),
        ]
        for response in responses:
            with self.subTest():
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
