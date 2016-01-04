from django.contrib import admin
from django.conf import settings
from django.db import models

from hvad.admin import TranslatableAdmin, TranslatableStackedInline

from easy_cms.models import Placeholder, Content


class PlaceholderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'get_sites', 'view_name')
    list_filter = ('view_name', 'sites__domain')
    filter_horizontal = ('sites',)

    def get_sites(self, obj):
        return ', '.join([s.domain for s in obj.sites.all()])


class ContentInline(TranslatableStackedInline):
    model = Content
    extra = 0
    fields = ['name', 'description', 'url', 'image', 'title', 'tagline',
              'content']


class ContentAdmin(TranslatableAdmin):
    list_display = ('id', 'name', 'get_sites', 'created_at')
    list_filter = ('sites__domain',)
    filter_horizontal = ('sites',)
    inlines = [ContentInline]
    if getattr(settings, 'CMS_MARKDOWN_ENABLED', False):
        try:
            from django_markdown.widgets import MarkdownWidget
            formfield_overrides = {
                models.TextField: {'widget': MarkdownWidget},
            }
        except ImportError:
            pass

    def get_sites(self, obj):
        return ', '.join([s.domain for s in obj.sites.all()])


admin.site.register(Placeholder, PlaceholderAdmin)
admin.site.register(Content, ContentAdmin)
