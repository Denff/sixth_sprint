from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import NUMBER_OF_CHARACTERS, Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у модели корректно работает __str__."""
        error_message = f"Вывод не имеет {NUMBER_OF_CHARACTERS} символов"
        self.assertEqual(self.post.__str__(),
                         self.post.text[:NUMBER_OF_CHARACTERS],
                         error_message)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у модели корректно работает __str__."""
        error_message = 'Вывод метода __str__ работает некорректно'
        self.assertEqual(
            self.group.__str__(), self.group.title, error_message)
