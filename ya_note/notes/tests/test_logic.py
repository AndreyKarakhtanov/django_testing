from http import HTTPStatus

from django.contrib.auth import get_user_model
from pytils.translit import slugify

from .test_base import TestBase
from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestBase):
    """Тестирование логики создания заметок."""
    @classmethod
    def setUpTestData(cls):
        """Подготовка фиксур"""
        super(TestNoteCreation, cls).setUpTestData()
        cls.form_data = {
            'title': cls.NEW_NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT,
            'slug': cls.NEW_NOTE_SLUG
        }

    def test_anonymous_user_cant_create_note(self):
        """Тест: Анонимный пользователь не может создать заметку."""
        notes_count = Note.objects.count()
        self.client.post(self.NOTES_ADD_URL, data=self.form_data)
        new_notes_count = Note.objects.count()
        self.assertEqual(new_notes_count, notes_count)

    def test_user_can_create_note(self):
        """Тест: Залогиненный пользователь может создать заметку."""
        Note.objects.all().delete()
        notes_count = Note.objects.count()
        response = self.author_client.post(
            self.NOTES_ADD_URL,
            data=self.form_data
        )
        self.assertRedirects(response, self.NOTES_SUCCESS_URL)
        new_notes_count = Note.objects.count()
        self.assertEqual(new_notes_count, notes_count + 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(new_note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(new_note.author, self.author)

    def test_unique_slug(self):
        """Тест: Невозможно создать две заметки с одинаковым slug."""
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(
            self.NOTES_ADD_URL,
            data=self.form_data
        )
        self.assertFormError(
            response, 'form', 'slug', errors=(self.note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        """Тест: Если при создании заметки не заполнен slug,
        то он формируется автоматически,
        с помощью функции pytils.translit.slugify.
        """
        Note.objects.all().delete()
        self.form_data.pop('slug')
        response = self.author_client.post(
            self.NOTES_ADD_URL,
            data=self.form_data
        )
        self.assertRedirects(response, self.NOTES_SUCCESS_URL)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestNoteEditDelete(TestBase):
    """Тестирование логики редактирования и удаления заметок."""
    @classmethod
    def setUpTestData(cls):
        """Подготовка фиксур"""
        super(TestNoteEditDelete, cls).setUpTestData()
        cls.form_data = {
            'title': cls.NEW_NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT,
            'slug': cls.NEW_NOTE_SLUG
        }
        cls.NOTE_SLUG = cls.note.slug

    def test_author_can_edit_note(self):
        """Тест: Пользователь может редактировать свои заметки."""
        response = self.author_client.post(
            self.NOTES_EDIT_URL,
            data=self.form_data
        )
        self.assertRedirects(response, self.NOTES_SUCCESS_URL)
        edited_note = Note.objects.get(id=self.note.id)
        self.assertEqual(edited_note.title, self.form_data['title'])
        self.assertEqual(edited_note.text, self.form_data['text'])
        self.assertEqual(edited_note.slug, self.form_data['slug'])
        self.assertEqual(edited_note.author, self.author)

    def test_user_cant_edit_note_of_another_user(self):
        """Тест: Пользователь не может редактировать чужие заметки."""
        response = self.reader_client.post(
            self.NOTES_EDIT_URL,
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        edited_note = Note.objects.get(id=self.note.id)
        self.assertEqual(edited_note.title, self.note.title)
        self.assertEqual(edited_note.text, self.note.text)
        self.assertEqual(edited_note.slug, self.note.slug)
        self.assertEqual(edited_note.author, self.author)

    def test_author_can_delete_note(self):
        """Тест: Пользователь может удалять свои заметки."""
        notes_count = Note.objects.count()
        response = self.author_client.delete(self.NOTES_DELETE_URL)
        self.assertRedirects(response, self.NOTES_SUCCESS_URL)
        new_notes_count = Note.objects.count()
        self.assertEqual(new_notes_count, notes_count - 1)

    def test_user_cant_delete_note_of_another_user(self):
        """Тест: Пользователь не может удалять чужие заметки."""
        notes_count = Note.objects.count()
        response = self.reader_client.delete(self.NOTES_DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        new_notes_count = Note.objects.count()
        self.assertEqual(new_notes_count, notes_count)
