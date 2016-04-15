def generic_autodiscover(module_name):
    """
    I have copy/pasted this code too many times...Dynamically autodiscover a
    particular module_name in a django project's INSTALLED_APPS directories,
    a-la django admin's autodiscover() method.
    Usage:
        generic_autodiscover('commands') <-- find all commands.py and load 'em
    """
    from importlib import import_module
    from django.core.exceptions import ImproperlyConfigured
    import imp
    import sys
    from django.conf import settings

    for app in settings.INSTALLED_APPS:
        try:
            import_module(app)
            app_path = sys.modules[app].__path__
        except AttributeError:
            continue
        try:
            imp.find_module(module_name, app_path)
        except ImportError:
            continue
        try:
            import_module('%s.%s' % (app, module_name))
        except ImproperlyConfigured:
            continue
        app_path = sys.modules['%s.%s' % (app, module_name)]
