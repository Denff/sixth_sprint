from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.another_new_group = Group.objects.create(
            title='Тестовая другая новая группа',
            slug='test-group',
            description='Описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый старый текст',
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_create(self):
        """Проверка формы создания поста"""

        posts_count = Post.objects.count()
        form_data = {'text': 'Текст в поле',
                     'group': self.group.id}
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True)
        self.assertRedirects(
            response, reverse('posts:profile', kwargs={'username': 'test'})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(
            Post.objects.filter(
                text='Текст в поле',
                group=self.group.id,
                author=self.user
            ).exists(),
            'Данные поста не совпадают')
        self.assertEqual(
            Post.objects.count(),
            posts_count + 1,
            'Поcт не добавлен в базу данных')

    def test_edit_post(self):
        """Проверка формы редактирования поста"""

        old_text = self.post

        form_data = {
            'text': 'Новый текст записанный в форму',
            'group': self.another_new_group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': old_text.id}),
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(
            Post.objects.filter(
                group=self.another_new_group.id,
                author=self.user,
                pub_date=self.post.pub_date
            ).exists(),
            'Данные поста не изменились')
        error_msg1 = ('Неавторизованный пользователь',
                      'не может изменить содержание поста')
        error_msg2 = ('Неавторизованный пользователь',
                      'не может изменить группу поста')
        self.assertNotEqual(
            old_text.text, form_data['text'], error_msg1)
        self.assertNotEqual(
            old_text.group, form_data['group'], error_msg2)
