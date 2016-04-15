import json

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.http import Http404, HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.template import loader, RequestContext
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator

from easy_cms.models import Content
from easy_cms.serializers import serialize_staticpage


DEFAULT_TEMPLATE = 'cms/staticpages/default.html'


# copied from django's FlatpageFallbackMiddleware
class StaticPagesFallbackMiddleware(object):
    @method_decorator(csrf_protect)
    def render_staticpage(self, request, staticpage):
        if request.is_ajax():
            return HttpResponse(json.dumps(serialize_staticpage(staticpage)),
                                content_type="application/json")

        # If registration is required for accessing this page, and the user
        # isn't logged in, redirect to the login page.
        if staticpage.template_name:
            t = loader.select_template(
                (staticpage.template_name, DEFAULT_TEMPLATE))
        else:
            t = loader.get_template(DEFAULT_TEMPLATE)

        # To avoid having to always use the "|safe" filter in flatpage
        # templates, mark the title and content as already safe
        # (since they are raw HTML content in the first place).
        staticpage.title = mark_safe(staticpage.title)
        staticpage.content = mark_safe(staticpage.content)

        c = RequestContext(request, {'staticpage': staticpage})
        return HttpResponse(t.render(c))

    def staticpage(self, request, url):
        if not url.startswith('/'):
            url = '/' + url
        site_id = get_current_site(request).id
        lang = request.LANGUAGE_CODE
        try:
            staticpage = get_object_or_404(Content.objects.language(lang),
                                           url__exact=url,
                                           site__id__exact=site_id)
        except Http404:
            if not url.endswith('/') and settings.APPEND_SLASH:
                url += '/'
                staticpage = get_object_or_404(Content.objects.language(lang),
                                               url__exact=url,
                                               site__id__exact=site_id)
                return HttpResponsePermanentRedirect('%s/' % request.path)
            else:
                raise
        return self.render_staticpage(request, staticpage)

    def process_response(self, request, response):
        if response.status_code != 404:
            return response
        try:
            return self.staticpage(request, request.path_info)
        # Return the original response if any errors happened. Because this
        # is a middleware, we can't assume the errors will be caught elsewhere.
        except Http404:
            return response
        except:
            if settings.DEBUG:
                raise
            return response
