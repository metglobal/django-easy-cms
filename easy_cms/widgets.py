from easy_cms import widget


@widget
def content(context, name, **kwargs):
    from django.contrib.sites.models import Site
    from easy_cms.models import Content
    try:
        site = Site.objects.get_current()
        obj = Content.objects.prefetch_related('children')\
            .get(name=name, site=site)
        return {'content': obj}, obj.template_name
    except Content.DoesNotExist:
        return {}, None


@widget
def template_widget(context, template_name=None, **kwargs):
    return kwargs, template_name
