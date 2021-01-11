from django.contrib.auth import login, logout

from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Prefetch, Exists, OuterRef
from datetime import datetime
from django.shortcuts import render, redirect

from django.views import View
from django.contrib.auth.forms import AuthenticationForm

from manager.forms import BookForm, CustomAuthenticationForm, CommentForm, CustomUserCreationForm, BookUpForm
from manager.models import LikeCommentUser, Comment, Book, Genre, GitInfo
from manager.models import LikeBookUser as RateBookUser

from pip._vendor.requests import post, get
from manager.tasks import git_info


class MyPage(View):
    def get(self, request):
        context = {}
        genres_all = Genre.objects.all()
        books = Book.objects.prefetch_related("authors", "genres")
        if request.user.is_authenticated:
            is_owner = Exists(
                User.objects.filter(books=OuterRef('pk'), id=request.user.id))
            is_liked = Exists(
                User.objects.filter(liked_books=OuterRef('pk'), id=request.user.id))
            books = books.annotate(is_owner=is_owner, is_liked=is_liked)
        books = books.order_by("-rate", "date")
        context['range'] = range(1, 6)
        context['form'] = BookForm()
        context['login_form'] = AuthenticationForm()
        context['genres_all'] = genres_all
        # context['books'] = books

        paginator = Paginator(books, 3)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj

        return render(request, "index.html", context)


class LoginView(View):
    def get(self, request):
        return render(request, "login.html", {"form": CustomAuthenticationForm})

    def post(self, request):
        user = AuthenticationForm(data=request.POST)
        if user.is_valid():
            login(request, user.get_user())
            return redirect("the-personal-page")
        messages.error(request, user.error_messages)
        return redirect("login")


class RegisterView(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, "register.html", {"form": form})

    def post(self, request):
        form = CustomUserCreationForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
        messages.error(request, form.error_messages)
        return redirect("register")


def logout_user(request):
    logout(request)
    return redirect("the-main-page")


class AddLike2Comment(View):
    def get(self, request, slug, id_comment, location=None):
        if request.user.is_authenticated:
            LikeCommentUser.objects.create(user=request.user, comment_id=id_comment)
        if location is None:
            return redirect("the-main-page")
        return redirect("book-detail", slug=slug)


class AddRate2Book(View):
    def get(self, request, slug, rate, location=None):
        if request.user.is_authenticated:
            RateBookUser.objects.create(user=request.user, book_id=slug, rate=rate)
        if location is None:
            return redirect("the-main-page")
        return redirect("book-detail", slug=slug)


class BookDetail(View):
    def get(self, request, slug):
        comment_query = Comment.objects.select_related("author")
        if request.user.is_authenticated:
            is_owner = Exists(
                User.objects.filter(users_comments=OuterRef('pk'), id=request.user.id))
            is_liked = Exists(
                User.objects.filter(liked_comments=OuterRef('pk'), id=request.user.id))
            comment_query = comment_query.annotate(is_owner=is_owner, is_liked=is_liked)
        comments = Prefetch("comments", comment_query)
        book = Book.objects.prefetch_related("authors", comments).annotate(
            count_comment=Count("comments"))
        if request.user.is_authenticated:
            is_owner = Exists(
                User.objects.filter(books=OuterRef('pk'), id=request.user.id))
            is_liked = Exists(
                User.objects.filter(liked_books=OuterRef('pk'), id=request.user.id))
            book = book.annotate(is_owner=is_owner, is_liked=is_liked)
        book = book.get(slug=slug)

        if request.user.is_authenticated:
            users = User.objects.all()
            read_user = request.user
            if users.filter(username=read_user).exists():
                read_users_id = users.get(username=read_user).id
                book.read_users.add(read_users_id)
                book.save()

        return render(request, "book_detail.html", {
            "book": book,
            "range": range(1, 6),
            "form": CommentForm()
        })


class GenreFilter(View):
    def get(self, request, genre):
        context = {}
        genres_all = Genre.objects.all()
        genre = genres_all.get(genre=genre)
        books = Book.objects.prefetch_related("authors", "genres")
        if request.user.is_authenticated:
            is_owner = Exists(
                User.objects.filter(books=OuterRef('pk'), id=request.user.id))
            is_liked = Exists(
                User.objects.filter(liked_books=OuterRef('pk'), id=request.user.id))
            books = books.annotate(is_owner=is_owner, is_liked=is_liked)
        context['books'] = books.filter(genres=genre).order_by("-rate", "date")
        context['range'] = range(1, 6)
        context['form'] = BookForm()
        context['login_form'] = AuthenticationForm()
        context['genres_all'] = genres_all
        context['genre'] = genre
        return render(request, "books_genre_filter.html", context)


class AddBook(View):
    def post(self, request):
        if request.user.is_authenticated:
            bf = BookForm(request.POST, request.FILES)
            if bf.is_valid():
                book = bf.save(commit=True)
                book.authors.add(request.user)
                book.save()
                return redirect("the-main-page")
        messages.error(request, "книга с таким slug уже существует!!! измените slug")
        return redirect("the-main-page")


def book_delete(request, slug):
    if request.user.is_authenticated:
        book = Book.objects.get(slug=slug)
        if request.user in book.authors.all():
            book.delete()
    return redirect("the-main-page")


class UpdateBook(View):
    def get(self, request, slug):
        if request.user.is_authenticated:
            book = Book.objects.get(slug=slug)
            if request.user in book.authors.all():
                form = BookUpForm(instance=book)
                return render(
                    request,
                    "update_book.html",
                    {"form": form, "slug": book.slug, "book": book}
                )
        return redirect("the-main-page")

    def post(self, request, slug):
        if request.user.is_authenticated:
            book = Book.objects.get(slug=slug)
            if request.user in book.authors.all():
                bf = BookUpForm(instance=book, data=request.POST, files=request.FILES)
                if bf.is_valid():
                    bf.save(commit=True)
                    book.save()
                    return redirect("book-detail", slug=slug)
        messages.error(request, "книга не была обновлена")
        return redirect("book-detail", slug=slug)


class UpdateBookAuthor(View):
    def post(self, request, slug):
        if request.user.is_authenticated:
            book = Book.objects.get(slug=slug)
            users = User.objects.all()
            if request.user in book.authors.all():
                author = request.POST['text']
                if users.filter(username=author).exists():
                    author_id = users.get(username=author).id
                    book.authors.add(author_id)
                    book.save()
                    return redirect("book-detail", slug=slug)
        messages.error(request, "книга не была обновлена")
        return redirect("book-detail", slug=slug)


class AddComment(View):
    def post(self, request, slug, location=None):
        if request.user.is_authenticated:
            cf = CommentForm(data=request.POST)
            comment = cf.save(commit=False)
            comment.book_id = Book.objects.get(slug=slug).slug
            comment.author = request.user
            comment = cf.save(commit=True)
            comment.save()
        return redirect("book-detail", slug=slug)


def comment_delete(request, slug, id_comment):
    if request.user.is_authenticated:
        comment = Comment.objects.get(id=id_comment)
        if request.user == comment.author:
            comment.delete()
    return redirect("book-detail", slug=slug)


class UpdateComment(View):
    def get(self, request, slug, id_comment):
        if request.user.is_authenticated:
            comment = Comment.objects.get(id=id_comment)
            if request.user == comment.author:
                form = CommentForm(instance=comment)
                return render(
                    request,
                    "update_comment.html",
                    {"form": form, "slug": slug, "id_comment": id_comment}
                )
        return redirect("book-detail", slug=slug)

    def post(self, request, slug, id_comment):
        if request.user.is_authenticated:
            comment = Comment.objects.get(id=id_comment)
            if request.user == comment.author:
                cf = CommentForm(instance=comment, data=request.POST)
                if cf.is_valid():
                    cf.save(commit=True)
        return redirect("book-detail", slug=slug)


def personal_view(request):
    GIT_CLIENT_ID = "67034e1bad91d3ff3c17"
    url = f"https://github.com/login/oauth/authorize?client_id={GIT_CLIENT_ID}"

    g_info = 0
    books = Book.objects.prefetch_related("read_users")
    if request.user.is_authenticated:
        books = books.filter(read_users=request.user)

        g_info = GitInfo.objects.all().filter(user_id=request.user)  #

    return render(request, "personal_page.html", {
        "url": url,
        "my_books": books,
        "g_info": g_info,
        }
    )


def git_callback(request):
    GIT_CLIENT_ID = "67034e1bad91d3ff3c17"
    GIT_CLIENT_SECRET = "2723cc7ab60c2a1ed7208182bb896909362b88df"
    code = request.GET.get("code")
    url = f"https://github.com/login/oauth/access_token?" \
          f"client_id={GIT_CLIENT_ID}&client_secret={GIT_CLIENT_SECRET}&code={code}"
    response = post(url, headers={'Accept': 'application/json'})
    # r = response.json()
    access_token = response.json()['access_token']
    url = "https://api.github.com/user"
    response = get(url, headers={'Authorization': f'token {access_token}'})
    r = response.json()
    login = r['login']
    count_repos = r['public_repos']
    url = f"https://api.github.com/users/{login}/repos"
    response = get(url)
    repos = [i['name'] for i in response.json()]

    books = Book.objects.prefetch_related("read_users")
    if request.user.is_authenticated:
        books = books.filter(read_users=request.user)

    user_id = request.user.id  #
    git_data = GitInfo.objects.all().filter(user_id=user_id)
    if git_data:
        git_data.update(
            user_id=user_id,
            date=str(datetime.now()),
            result=str(repos),
            git_login=login
        )
    else:
        GitInfo.objects.create(user_id=user_id, date=str(datetime.now()), result=str(repos), git_login=login)

    return render(request, "personal_page.html", {
        'repos_list': repos,
        # "r": r,
        "my_books": books,
        "login": login,
        "count_repos": count_repos,
    })