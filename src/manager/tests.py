from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from slugify import slugify
from manager.models import Book


class TestMyAppPlease(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("test_name")
        self.user1 = User.objects.create_user("test_name1")
        self.user2 = User.objects.create_user("test_name2")

    def test_add_book(self):
        self.client.force_login(self.user)
        url = reverse("add-book")
        data = {
            'slug': 'test-title',
            'title': "test title",
            'text': 'test text'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302, msg="is not redirected")
        self.assertTrue(Book.objects.exists(), msg="book is not created")
        # book = Book.objects.first()
        # self.assertEqual(book.title, data['title'])
        # self.assertEqual(book.text, data['text'])
        # self.assertEqual(book.slug, slugify(data['title']))
        # self.assertEqual(book.authors.first(), self.user)
        # self.client.logout()
        # data = {
        #     'title': "test title2",
        #     'text': 'test text'
        # }
        # response = self.client.post(url, data)
        # self.assertEqual(response.status_code, 302, msg="is not redirected")
        # self.assertEqual(Book.objects.count(), 1, msg="created book without author")
