from django.forms import ModelForm, TextInput, Textarea, CharField, PasswordInput
from manager.models import Comment
from manager.models import Book
from django.contrib.auth.forms import AuthenticationForm, UsernameField, UserCreationForm


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        pass

    username = UsernameField(widget=TextInput(attrs={"class": "form-control"}))
    password1 = CharField(
        label="Password",
        strip=False,
        widget=PasswordInput(attrs={'autocomplete': 'new-password', "class": "form-control"})
    )
    password2 = CharField(
        label="Password confirmation",
        widget=PasswordInput(attrs={'autocomplete': 'new-password', "class": "form-control"}),
        strip=False
    )


class CustomAuthenticationForm(AuthenticationForm):
    username = UsernameField(
        widget=TextInput(attrs={'autofocus': True, "class": "form-control"}))
    password = CharField(
        label="Password",
        strip=False,
        widget=PasswordInput(attrs={'autocomplete': 'current-password', 'class': 'form-control'})
    )


class BookForm(ModelForm):
    class Meta:
        model = Book
        fields = ['slug',
                  'title',
                  'text',
                  'genres',
                  'book_img'
                  ]
        widgets = {
            "slug": TextInput(attrs={"class": "form-control"}, ),
            "title": TextInput(attrs={"class": "form-control"}),
            "text": Textarea(attrs={"class": "form-control", "rows": 5, "cols": 50}),
        }
        help_texts = {
            "slug": "",
            "title": "",
            "text": "",
        }
        msg = ""


class BookUpForm(ModelForm):
    class Meta:
        model = Book
        fields = [
            'text',
            'genres',
            'authors',
            'book_img'
        ]
        widgets = {
            "text": Textarea(attrs={"class": "form-control", "rows": 5, "cols": 50})
        }
        help_texts = {
            "text": ""
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = [
            'text'
        ]
        widgets = {
            "text": Textarea(attrs={"class": "form-control", "rows": 5, "cols": 50}),
        }
        help_texts = {
            "text": "",
        }


class AuthorAddForm(ModelForm):
    class Meta:
        model = Book
        fields = [
            'authors'
        ]
        widgets = {
            "authors": TextInput(attrs={"class": "form-control"}),
        }
        help_texts = {
            "authors": "",
        }

