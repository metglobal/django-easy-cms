from easy_cms.utils import generic_autodiscover

registry = {}


def widget(f):
    registry[f.__name__] = f
    return f

generic_autodiscover('widgets')
