from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post
from ..utils import NUMBER_OF_POSTS

User = get_user_model()
TEST_NUMBER_OF_POSTS: int = 18


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='test')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            pub_date='date',
            group=cls.group,
            author=cls.user
        )

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self) -> None:
        """
        URL-адрес использует соответствующий шаблон.
        """
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug':
                        self.group.slug}): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username':
                        self.user.username}): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id':
                        self.post.id}): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id':
                        self.post.id}): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def check_context_contains_page_or_post(self, context, post) -> None:
        """Проверка контекста для index, post_detail, group_list"""

        if post:
            post = context
        else:
            post = context[0]
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.pub_date, self.post.pub_date)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.group, self.post.group)

    def test_index_page_show_correct_context(self) -> None:
        """
        Cоответствует ли ожиданиям словарь context,
        передаваемый в шаблон index.
        """
        response = self.guest_client.get(
            reverse('posts:index'))
        self.check_context_contains_page_or_post(
            response.context['page_obj'], False)

    def test_post_detail_page_show_correct_context(self) -> None:
        """
        Cоответствует ли ожиданиям словарь context,
        передаваемый в шаблон post_detail.
        """
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}))
        self.check_context_contains_page_or_post(
            response.context['post'], True)

    def test_group_list_page_show_correct_context(self) -> None:
        """
        Cоответствует ли ожиданиям словарь context,
        передаваемый в шаблон group_list.
        """
        response = self.guest_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}))
        self.check_context_contains_page_or_post(
            response.context['page_obj'], False)

    def test_post_create_page_show_correct_context(self) -> None:
        """
        Cоответствует ли ожиданиям словарь context,
        передаваемый в шаблон post_create.
        """
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_added_correctly(self) -> None:
        """Пост при создании добавлен корректно"""

        post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group)
        response_index = self.authorized_client.get(
            reverse('posts:index'))
        response_group = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}))
        response_profile = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user.username}))
        self.assertIn(post,
                      response_index.context['page_obj'],
                      'поста нет на главной')
        self.assertIn(post,
                      response_group.context['page_obj'],
                      'поста нет в группе')
        self.assertIn(post,
                      response_profile.context['page_obj'],
                      'поста нет в профиле')

    def test_post_added_correctly_and_no_post_in_another_group(self) -> None:
        """Пост при создании добавлен корректно и его нет в другой группе"""

        post = Post.objects.create(text='Тестовый текст',
                                   author=self.user,
                                   group=self.group)
        Group.objects.create(title='Группа 2',
                             slug='test_group2')
        response_group2 = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': 'test_group2'}))
        group2 = response_group2.context['page_obj']
        message = 'ошибка, пост в другой группе'
        self.assertNotIn(post, group2, message)


class PaginatorViewsTest(TestCase):
    ERROR_MESSAGE1 = (
        'Ошибка: количество постов на первой ',
        f'странице меньше {NUMBER_OF_POSTS}!')
    ERROR_MESSAGE2 = (
        'Ошибка: количество постов ',
        f'больше {NUMBER_OF_POSTS * 2}!')

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='test')
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group')
        bulk_post: list = []
        for i in range(TEST_NUMBER_OF_POSTS):
            bulk_post.append(Post(
                text=f'Тестовый текст {i}',
                group=self.group,
                author=self.user))
        Post.objects.bulk_create(bulk_post)

    def test_posts_on_pages_for_guest_client(self) -> None:
        """
        Проверка количества постов на первой и второй страницах
        для неавторизованного пользователя
        """
        pages: tuple = (reverse('posts:index'),
                        reverse('posts:profile',
                                kwargs={'username': f'{self.user.username}'}),
                        reverse('posts:group_list',
                                kwargs={'slug': f'{self.group.slug}'}))
        for page in pages:
            response1 = self.guest_client.get(page)
            response2 = self.guest_client.get(page + '?page=2')
            count_posts1 = len(response1.context['page_obj'])
            count_posts2 = len(response2.context['page_obj'])
            self.assertEqual(
                count_posts1, NUMBER_OF_POSTS,
                self.ERROR_MESSAGE1)
            self.assertEqual(
                count_posts2,
                TEST_NUMBER_OF_POSTS - NUMBER_OF_POSTS,
                self.ERROR_MESSAGE2)

    def test_posts_on_pages_for_authorized_client(self) -> None:
        """
        Проверка количества постов на первой и второй страницах
        для авторизованного пользователя
        """
        pages: tuple = (reverse('posts:index'),
                        reverse('posts:profile',
                                kwargs={'username': f'{self.user.username}'}),
                        reverse('posts:group_list',
                                kwargs={'slug': f'{self.group.slug}'}))
        for page in pages:
            response1 = self.authorized_client.get(page)
            response2 = self.authorized_client.get(page + '?page=2')
            count_posts1 = len(response1.context['page_obj'])
            count_posts2 = len(response2.context['page_obj'])
            self.assertEqual(
                count_posts1, NUMBER_OF_POSTS,
                self.ERROR_MESSAGE1)
            self.assertEqual(
                count_posts2,
                TEST_NUMBER_OF_POSTS - NUMBER_OF_POSTS,
                self.ERROR_MESSAGE2)
