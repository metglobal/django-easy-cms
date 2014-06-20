from django.conf import settings
from django.contrib.sites.models import get_current_site
from django.http import Http404, HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.template import loader, RequestContext
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_protect

from easy_cms.models import Content


# copied from django's FlatpageFallbackMiddleware
class StaticPagesFallbackMiddleware(object):
    def process_response(self, request, response):
        if response.status_code != 404:
            return response
        try:
            return staticpage(request, request.path_info)
        # Return the original response if any errors happened. Because this
        # is a middleware, we can't assume the errors will be caught elsewhere.
        except Http404:
            return response
        except:
            if settings.DEBUG:
                raise
            return response


DEFAULT_TEMPLATE = 'cms/staticpages/default.html'


def staticpage(request, url):
    """
    Public interface to the flat page view.

    Models: `flatpages.flatpages`
    Templates: Uses the template defined by the ``template_name`` field,
        or :template:`flatpages/default.html` if template_name is not defined.
    Context:
        flatpage
            `flatpages.flatpages` object
    """
    if not url.startswith('/'):
        url = '/' + url
    site_id = get_current_site(request).id
    lang = request.LANGUAGE_CODE
    try:
        f = get_object_or_404(
            Content.objects.language(lang), url__exact=url,
            site__id__exact=site_id)
    except Http404:
        if not url.endswith('/') and settings.APPEND_SLASH:
            url += '/'
            f = get_object_or_404(
                Content.objects.language(lang), url__exact=url,
                site__id__exact=site_id)
            return HttpResponsePermanentRedirect('%s/' % request.path)
        else:
            raise
    return render_staticpage(request, f)


@csrf_protect
def render_staticpage(request, f):
    """
    Internal interface to the flat page view.
    """
    # If registration is required for accessing this page, and the user isn't
    # logged in, redirect to the login page.
    if f.template_name:
        t = loader.select_template((f.template_name, DEFAULT_TEMPLATE))
    else:
        t = loader.get_template(DEFAULT_TEMPLATE)

    # To avoid having to always use the "|safe" filter in flatpage templates,
    # mark the title and content as already safe (since they are raw HTML
    # content in the first place).
    f.title = mark_safe(f.title)
    f.content = mark_safe(f.content)

    c = RequestContext(request, {
        'staticpage': f,
    })
    response = HttpResponse(t.render(c))
    return response
