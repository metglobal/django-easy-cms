django-easy-cms
===============

* Add 'redactor' and 'easy_cms' to INSTALLED_APPS.

```python
INSTALLED_APPS = (
    # ...
    'redactor',
    'easy_cms',
    # ...
)
```

* Add url(r'^redactor/', include('redactor.urls')), to urls.py

```python
urlpatterns = [
    # ...
    url(r'^redactor/', include('redactor.urls')),
    # ...
]
```
