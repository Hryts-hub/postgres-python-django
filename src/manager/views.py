from django.contrib.auth import login, logout

from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator  #
from django.db.models import Count, Prefetch, Exists, OuterRef
from django.shortcuts import render, redirect

from django.views import View
from django.contrib.auth.forms import AuthenticationForm

from manager.forms import BookForm, CustomAuthenticationForm, CommentForm, CustomUserCreationForm, BookUpForm
from manager.models import LikeCommentUser, Comment, Book, Genre
from manager.models import LikeBookUser as RateBookUser

import json
import requests
import webbrowser
import base64
from django.http import HttpResponse


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
        books = books.order_by("-rate", "date")  #
        context['range'] = range(1, 6)
        context['form'] = BookForm()
        context['login_form'] = AuthenticationForm()
        context['genres_all'] = genres_all
        # context['books'] = books  #

        paginator = Paginator(books, 3)  # Show 3 books per page.
        page_number = request.GET.get('page')  #
        page_obj = paginator.get_page(page_number)  #
        context['page_obj'] = page_obj  #

        return render(request, "index.html", context)


class LoginView(View):
    def get(self, request):
        return render(request, "login.html", {"form": CustomAuthenticationForm})

    def post(self, request):
        user = AuthenticationForm(data=request.POST)
        if user.is_valid():
            login(request, user.get_user())
            return redirect("the-main-page")
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
            book = book.annotate(is_owner=is_owner, is_liked=is_liked).get(slug=slug)
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


# class MyTestView(View):
#     def get(self, request):
#         return render(request, "mytest.html",)

client_id = '67034e1bad91d3ff3c17'
client_secret = 'c710b86e7855508ba8df41cd147d6e487857f9fe'
redirect_uri = 'http://127.0.0.1:8000/shop/mytest/'
login = 'Hryts-hub'
scope = 'public_repo'
# b64_id_secret = base64.b64encode(bytes(client_id + ':' + client_secret, 'utf-8')).decode('utf-8')
# allow_signup = False

def XeroFirstAuth(request):
    # 1. Send a user to authorize your app
    auth_url = ('''https://github.com/login/oauth/authorize?''' +
                '''response_type=code''' +
                '''&client_id=''' + client_id +
                '''&redirect_uri=''' + redirect_uri +
                '''&scope=''' + scope +
                '''&state=123''' +
                '''&allow_signup=False ''')
    webbrowser.open_new(auth_url)
    # return redirect(auth_url)

    # 2. Users are redirected back to you with a code

    auth_res_url = request.GET
    # auth_res_url = "http://127.0.0.1:8000/shop/mytest/?code=cfa0aa657e7f29afd126&state=123"  # request.GET
    # return HttpResponse(auth_res_url)
    #
    # start_number = auth_res_url.find('code=') + len('code=')
    # end_number = auth_res_url.find('&scope')
    # auth_code = auth_res_url[start_number:end_number]
    auth_code = "8506b9a057ac1e5adc87" #auth_res_url[start_number:end_number]
    # print(auth_code)
    # print('\n')

    # 3. Exchange the code
    exchange_code_url = 'https://github.com/login/oauth/access_token'
    response = requests.post(exchange_code_url,
                             headers={
                                 'Authorization': 'token OAUTH-TOKEN'
                             },
                             data={
                                 'client_id': client_id,
                                 'client_secret': client_secret,
                                 'code': auth_code,
                                 # 'redirect_uri': redirect_uri,
                                 # 'state': "123"
                             })
    json_response = response.json()
    a = json_response['access_token']
    return HttpResponse(a)
    json_response = response.json()
    # print(json_response)
    # print('\n')

    # 4. Receive your tokens
    return [json_response['access_token'], json_response['refresh_token']]
# render(request, "mytest.html",) #
