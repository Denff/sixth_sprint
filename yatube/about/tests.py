from http import HTTPStatus

from django.test import Client, TestCase


class StaticURLTests(TestCase):
    def setUp(self) -> None:
        self.guest_client = Client()

    def test_static_page(self) -> None:
        """Проверка доступа к страницам любому пользователю."""
        pages: tuple = ('/about/author/', '/about/tech/')
        for page in pages:
            response = self.guest_client.get(page)
            error_name: str = f'Ошибка: нет доступа к странице {page}'
            self.assertEqual(response.status_code, HTTPStatus.OK, error_name)
