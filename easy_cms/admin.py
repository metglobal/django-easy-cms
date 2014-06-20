from django.contrib import admin

from hvad.admin import TranslatableAdmin

from easy_cms.models import Placeholder, Content


class PlaceholderAdmin(admin.ModelAdmin):
    list_display = ('id', 'site', 'name', 'view_name')
    list_filter = ('view_name', 'site')


class ContentAdmin(TranslatableAdmin):
    list_display = ('id', 'site', 'name', 'description', 'created_at')
    list_filter = ('site',)


admin.site.register(Placeholder, PlaceholderAdmin)
admin.site.register(Content, ContentAdmin)
