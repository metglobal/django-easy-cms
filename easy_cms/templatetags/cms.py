import logging

from django import template
from django.core.cache import cache
from django.template.loader import render_to_string
from django.contrib.sites.models import Site

from easy_cms import registry

logger = logging.getLogger(__name__)

register = template.Library()


def widget(context, widget_name, template_name=None, **kwargs):
    language_code = context['request'].LANGUAGE_CODE
    caching = kwargs.get('caching')
    if caching:
        key = kwargs.get('caching_key') or caching['key'] + '-' + language_code
        cached = cache.get(key)
        if cached:
            return cached
    f = registry.get(widget_name)
    if not f:
        logger.warn('Widget "%s" not found' % widget_name)
        return ''
    context_data, _template_name = f(context, **kwargs)
    if not template_name:
        template_name = 'cms/widgets/%s.html' % (_template_name or widget_name)
    rendered = render_to_string(template_name, context_data)
    if caching:
        cache.set(key, rendered,
                  kwargs.get('caching_expire') or caching['expire'])
    return rendered


def placeholder(context, name):
    from easy_cms.models import Placeholder
    from django.core.urlresolvers import resolve
    site = Site.objects.get_current()
    try:
        container = Placeholder.objects.get(name=name, site=site)
        if container.view_name:
            request = context['request']
            match = resolve(request.path)
            if not container.view_name == match.view_name:
                logger.warn('Placeholder view names does not match.')
                return ''
    except Placeholder.DoesNotExist:
        logger.warn('Placeholder "%s" not found' % name)
        return ''

    widgets = []
    for c in container.widget_config:
        params = c.get('params', {})
        template_name = c.get('template_name')
        widgets.append(widget(context, c['name'], template_name, **params))

    placeholder_template_name = container.template_name
    if not placeholder_template_name:
        placeholder_template_name = 'cms/placeholders/%s.html' % name
    return render_to_string(placeholder_template_name, {
        'placeholder_name': name,
        'widgets': widgets
    })

register.simple_tag(takes_context=True)(widget)
register.simple_tag(takes_context=True)(placeholder)
