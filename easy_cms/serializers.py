from django.utils.safestring import mark_safe


def serialize_staticpage(staticpage):
    return {
        'title': staticpage.title,
        'content': mark_safe(staticpage.content),
        'description': staticpage.description,
        'tagline': staticpage.tagline,
        'image': staticpage.image.url if staticpage.image else None
    }
