from django.contrib import admin
from django.utils.html import format_html
from .models import *


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'author', 'date_created', 'download_link', 'is_active')
    list_editable = ('author', 'is_active')
    search_fields = ('title', 'author__fullname')
    list_filter = ('is_active', 'date_created')

    def download_link(self, obj):
        if obj.article:
            return format_html('<a href="/library/{}/download">Скачать</a>',
                               obj.slug)
        return "-"

    download_link.short_description = 'Ссылка для скачивания'


admin.site.register(Account)
admin.site.register(Keyword)
