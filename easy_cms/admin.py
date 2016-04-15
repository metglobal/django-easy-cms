from django.contrib import admin
from django.conf import settings
from django.db import models

from hvad.admin import TranslatableAdmin, TranslatableStackedInline

from easy_cms.models import Placeholder, Content


class PlaceholderAdmin(admin.ModelAdmin):
    list_display = ('id', 'site', 'name', 'view_name')
    list_filter = ('view_name', 'site')


class ContentAdmin(TranslatableAdmin):
    list_display = ('id', 'site', 'name', 'created_at')
    list_filter = ('site',)
    if getattr(settings, 'CMS_MARKDOWN_ENABLED', False):
        try:
            from django_markdown.widgets import MarkdownWidget
            formfield_overrides = {
                models.TextField: {'widget': MarkdownWidget},
            }
        except ImportError:
            pass


admin.site.register(Placeholder, PlaceholderAdmin)
admin.site.register(Content, ContentAdmin)
