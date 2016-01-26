import json
import logging

from django.http import Http404, HttpResponse, HttpResponsePermanentRedirect
from django.template import loader, RequestContext
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.contrib.sites.models import get_current_site
from django.conf import settings

from hvad.utils import combine

from easy_cms.serializers import serialize_staticpage
from easy_cms.models import ContentTranslation


logger = logging.getLogger(__name__)
fallback_language = 'en'
default_template = 'cms/staticpages/default.html'


class StaticPagesFallbackMiddleware(object):

    @method_decorator(csrf_protect)
    def render_staticpage(self, request, staticpage):
        if request.is_ajax():
            return HttpResponse(json.dumps(serialize_staticpage(staticpage)),
                                content_type="application/json")

        template = loader.select_template((staticpage.template_name,
                                           default_template))

        # To avoid having to always use the "|safe" filter in flatpage
        # templates, mark the title and content as already safe
        # (since they are raw HTML content in the first place).
        staticpage.title = mark_safe(staticpage.title)
        staticpage.content = mark_safe(staticpage.content)

        context = {
            'staticpage': staticpage,
            'children': staticpage.children.language(
                staticpage.language_code).all()
        }
        context = RequestContext(request, context)
        return HttpResponse(template.render(context))

    def get_staticpage(self, request, url):
        lang = request.LANGUAGE_CODE
        site = get_current_site(request)

        queryset = ContentTranslation.objects.filter(master__sites__id=site.id)
        staticpage = queryset.filter(url__exact=url).first()

        # if the request URL does not match any static page and
        # it doesn't end in a slash. Example: /about to /about/ redirect
        if not (staticpage and url.endswith('/')) and queryset.filter(
                url__exact=url + '/').exists() and settings.APPEND_SLASH:
            return HttpResponsePermanentRedirect('%s/' % request.path)

        # tr.domain/about to tr.domain/hakkimizda redirect
        if staticpage and staticpage.language_code != lang:
            translation = staticpage.master.translations.filter(
                language_code=lang).first()
            if translation:
                return HttpResponsePermanentRedirect(translation.url)

        # staticpage does not exists.
        if not staticpage or staticpage.language_code not in (
                lang, fallback_language):
            raise Http404

        staticpage = combine(staticpage, staticpage.master)
        return self.render_staticpage(request, staticpage)

    def process_response(self, request, response):
        if response.status_code != 404 or request.method != 'GET':
            return response

        try:
            return self.get_staticpage(request, request.path_info)
        except Http404:
            return response
        except Exception as e:
            logger.exception(e)
            if settings.DEBUG:
                raise
        return response
