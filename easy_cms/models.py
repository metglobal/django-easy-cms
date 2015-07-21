from jsonfield import JSONField
from hvad.models import TranslatableModel, TranslatedFields

from django.db import models
from django.contrib.sites.models import Site


class Placeholder(models.Model):

    name = models.SlugField(max_length=50)
    view_name = models.CharField(max_length=100, db_index=True,
                                 null=True, blank=True)
    widget_config = JSONField(default="[]")
    template_name = models.CharField(max_length=50, null=True, blank=True)

    # Foreign Keys
    site = models.ForeignKey('sites.Site')

    class Meta:
        unique_together = ('name', 'view_name')

    def __unicode__(self):
        return self.name


class Content(TranslatableModel):

    name = models.SlugField(max_length=50, unique=True)
    image = models.ImageField(upload_to='contents', null=True, blank=True)
    parent = models.ForeignKey('easy_cms.Content', null=True, blank=True,
                               related_name='children')
    created_at = models.DateTimeField(auto_now_add=True)
    template_name = models.CharField(max_length=50, null=True, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    # Translations
    translations = TranslatedFields(
        title=models.CharField(max_length=255, null=True, blank=True),
        tagline=models.CharField(max_length=255, null=True, blank=True),
        content=models.TextField(null=True, blank=True),
        description=models.CharField(max_length=500, null=True, blank=True),
        url=models.CharField(max_length=255, null=True, blank=True)
    )

    # Foreign Keys
    site = models.ForeignKey('sites.Site')

    class Meta:
        ordering = ['sort_order']

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.parent:
            try:
                self.site
            except Site.DoesNotExist:
                self.site = self.parent.site
        for child in self.children.all():
            if child.site != self.site:
                child.site = self.site
                child.save()
        super(Content, self).save(*args, **kwargs)
