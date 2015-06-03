import logging
import hashlib

from django import template
from django.core.cache import cache
from django.template.loader import render_to_string
from django.contrib.sites.models import Site

from easy_cms import registry

logger = logging.getLogger(__name__)

register = template.Library()


def widget(context, widget_name, template_name=None, cache_enabled=False,
           cache_timeout=None, cache_key=None, cache_key_prefix=None,
           vary_on_headers=None, vary_on_cookies=None, active=True,
           vary_on_sessions=None, **kwargs):
    if not active:
        return ''
    f = registry.get(widget_name)
    if not f:
        logger.warn('Widget "%s" not found' % widget_name)
        return ''
    request = context.get('request')
    assert request, """You need to add 'django.core.context_processors.request'
    in your TEMPLATE_CONTEXT_PROCESSORS settings.
    """
    output = None
    if cache_enabled:
        md5 = hashlib.md5()
        md5.update(cache_key_prefix or '')
        md5.update(cache_key or widget_name)
        md5.update(template_name or '')
        if vary_on_headers:
            for header in vary_on_headers:
                header_value = request.META.get(header)
                if header_value:
                    md5.update(header_value)
        if vary_on_cookies:
            for cookie in vary_on_cookies:
                cookie_value = request.COOKIES.get(cookie)
                if cookie_value:
                    md5.update(cookie_value)
        if vary_on_sessions:
            if hasattr(request, 'session'):
                for session in vary_on_sessions:
                    session_value = request.session.get(session)
                    if session_value:
                        md5.update(session_value)
        cache_key = md5.hexdigest()
        output = cache.get(cache_key)
        if output:
            logger.debug('"%s" is got from cache' % widget_name)

    if not output:
        context_data, _template_name = f(context, **kwargs)
        if not template_name:
            template_name = 'cms/widgets/%s.html' % (_template_name or
                                                     widget_name)
        context_data.update({'request': request})
        output = render_to_string(template_name, context_data)
        if cache_enabled:
            logger.debug('"%s" is put into cache' % widget_name)
            cache.set(cache_key, output, cache_timeout)
    return output


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
        widget_name = c['name']
        template_name = c.get('template_name')
        cache_enabled = c.get('cache_enabled')
        cache_timeout = c.get('cache_timeout')
        cache_key = c.get('cache_key')
        cache_key_prefix = c.get('cache_key_prefix')
        vary_on_headers = c.get('vary_on_headers')
        vary_on_cookies = c.get('vary_on_cookies')
        vary_on_sessions = c.get('vary_on_sessions')
        params = c.get('params', {})
        output = widget(context,
                        widget_name,
                        template_name=template_name,
                        cache_enabled=cache_enabled,
                        cache_timeout=cache_timeout,
                        cache_key=cache_key,
                        cache_key_prefix=cache_key_prefix,
                        vary_on_headers=vary_on_headers,
                        vary_on_cookies=vary_on_cookies,
                        vary_on_sessions=vary_on_sessions,
                        **params)
        widgets.append(output)

    placeholder_template_name = container.template_name
    if not placeholder_template_name:
        placeholder_template_name = 'cms/placeholders/%s.html' % name
    return render_to_string(placeholder_template_name, {
        'placeholder_name': name,
        'widgets': widgets
    })

register.simple_tag(takes_context=True)(widget)
register.simple_tag(takes_context=True)(placeholder)
