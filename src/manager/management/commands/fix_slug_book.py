from django.core.management.base import BaseCommand
from manager.models import Book, LikeBookUser, Comment#, SlugBook


class Command(BaseCommand):
    def handle(self, *args, **options):
        pass
        # books = Book.objects.prefetch_related("authors")
        #
        # arrSlugBook = [SlugBook(
        #     slug=b.slug,
        #     # id=b.id,
        #     title=b.title,
        #     date=b.date,
        #     text=b.text,
        #     # authors=b.authors.all(),
        #     # authors.add(b.authors.all()),
        #     count_rated_users=b.count_rated_users,
        #     count_all_stars=b.count_all_stars,
        #     rate=b.rate,
        #     # users_like=b.users_like,
        #         )
        #     for b in books
        #     ]
        #
        # SlugBook.objects.bulk_create(arrSlugBook)
        #

        #
        # query = Book.objects.all().values("slug", "id")
        # all_lbu = LikeBookUser.objects.all()
        # for book in query:
        #     new_set = all_lbu.filter(book_id=book['id'])
        #     for lbu in new_set:
        #         lbu.slug_id = book['slug']
        #         lbu.save()
        #

        # query = Book.objects.all().values("slug", "id")
        # all_comments = Comment.objects.all()
        # for book in query:
        #     comments = all_comments.filter(book_id=book['id'])
        #     for c in comments:
        #         c.slug_id = book['slug']
        #     Comment.objects.bulk_update(comments, ['slug_id'])


        # #  +
        # books = Book.objects.all()
        # tmp_books = SlugBook.objects.all()
        # for book in books:
        #     tmp_book = tmp_books.get(slug=book.slug)
        #     for author in book.authors.all():
        #         tmp_book.authors.add(author)
        #     tmp_book.save()

#  вариант из класса:

        # books = Book.objects.all()
        # arr = [
        #     TmpBook(
        #         title=b.title,
        #         text=b.text,
        #         date=b.date,
        #         rate=b.rate,
        #         count_rated_users=b.count_rated_users,
        #         count_all_stars=b.count_all_stars,
        #         slug=b.slug
        #     )
        #     for b in books
        # ]
        # TmpBook.objects.bulk_create(arr)
        # print("done-1")
        #
        # # - делаем отфильтрованный запрос к книгам -->
        # # QuerySet - список из словарей с результатом (ключами id+slug и их знач.),
        # # - делаем запрос к корректируемому классу -->
        # # QuerySet из списка объектов модели (<класс: объект>) с айдишниками лайка(коммента),
        # # - берем книгу из книг и находим книги в кор.классе с таким же id -->
        # # QuerySet из одного или нескольких объектов,
        # # (один юзер может лайкнуть(прокомментировать) несколько книг,
        # # книгу лайкают(комментируют) разные юзеры,
        # # объектов в current_lbu, столько, сколько юзеров + данную книгу.
        # # поэтому в соотв.табл. несколько раз может встретиться один и тот же book_id)
        # # - и этим книгам в кор.классе меняем поле слага на слаг из базовой книги.
        # # bulk_update - т.к. у книги id, slug - уникальные, однозначное соответствие.
        #
        # query = Book.objects.all().values("slug", "id")
        #
        # all_lbu = LikeBookUser.objects.all()
        # for book in query:
        #     current_lbu = all_lbu.filter(book_id=book['id'])
        #     for lbu in current_lbu:
        #         lbu.tmp_book_id = book['slug']
        #     LikeBookUser.objects.bulk_update(current_lbu, ['tmp_book_id'])
        #
        # # query = Book.objects.all().values("slug", "id")
        # all_comments = Comment.objects.all()
        # for book in query:
        #     current_comment = all_comments.filter(book_id=book['id'])
        #     for c in current_comment:
        #         c.tmp_book_id = book['slug']
        #     Comment.objects.bulk_update(current_comment, ['tmp_book_id'])
        # print("done-2")
        #
        # # Достаем книги, достаем тмп_книги,
        # # для книги из книг получаем тмп_книгу с слагом книги (1 книга - get).
        # # добавляем в авторы этой тмп_книги авторов из QuerySet авторов базовой книги.
        # # Чтобы дата не поменялась на сейчас, снова сохр.дату из базовой книги в тмп_книге
        # # save(), т.к. bulk_update не работает с M2M, у книги нет однознач.соотв. с автором.
        #
        # # books = Book.objects.all()
        # tmp_books = TmpBook.objects.all()
        # for book in books:
        #     tmp_book = tmp_books.get(slug=book.slug)
        #     for author in book.authors.all():
        #         tmp_book.authors.add(author)
        #     tmp_book.date = book.date
        #     tmp_book.save()
        # print("done-3")