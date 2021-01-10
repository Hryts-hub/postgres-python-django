from django.contrib import admin
from manager.models import Comment
from manager.models import Book
from manager.models import Genre
from manager.models import TableAggregate


class GenreAdmin(admin.ModelAdmin):
    pass


class CommentAdmin(admin.StackedInline):
    model = Comment
    extra = 2


class BookAdmin(admin.ModelAdmin):
    inlines = [CommentAdmin]
    readonly_fields = ["rate"]
    exclude = ['count_all_stars', "count_rated_users"]
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(Book, BookAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(TableAggregate)  #
