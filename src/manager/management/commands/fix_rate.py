from django.core.management.base import BaseCommand
from django.db.models import Sum, Count
from manager.models import Book


class Command(BaseCommand):
    def handle(self, *args, **options):
        books = Book.objects.annotate(
            tmp_all_stars=Sum("liked_user_table__rate"),
            tmp_rated_users=Count("liked_user_table")
        )
        for b in books:
            b.count_rated_users = b.tmp_rated_users
            b.count_all_stars = b.tmp_all_stars
            if b.tmp_rated_users:
                b.rate = b.tmp_all_stars / b.tmp_rated_users
            else:
                b.rate = 0
                b.count_all_stars = 0
        Book.objects.bulk_update(
            books,
            ["count_rated_users", "count_all_stars", "rate"],
            batch_size=4
        )