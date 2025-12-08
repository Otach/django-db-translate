===================
django-db-translate
===================

django-db-translate is an app with utilites to assist in project-wide translation.

With django-db-translate, you can:

1. Select fields from the database to include in `.po` files using `makemessages`

2. Edit translations directly in the admin site

Note
    This app is a work in progress and may break unexpectedly.

Quick start (Database Translations)
-----------------------------------

1. Add "django_db_translate" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...,
        "django_db_translate",
    ]

2. Add your project's locale directory to your LOCALE_PATHS setting like this::

    LOCALE_PATHS = [
        BASE_DIR / 'locale'
    ]

3. Run ``python manage.py migrate`` to create the models.

4. Add a `translatable_fields` class attribute to any model with fields you want to be translatable::

    class MyModel(models.Model):
        translatable_fields = ('txt_field',)
        txt_field = models.CharField()

5. Run ``python manage.py makemessages --all --include-db-strings`` to generate the `.po` files


Quick start (Admin Translation Editing)
---------------------------------------

1. Follow steps 1-3 from `Quick start (Database Translations)`

2. Include the custom admin site inplace of the standard admin site in your project's URLconf::

    from django_db_translate import admin
    urlpatterns = [
        ..., # Your other URLs here
        path("admin/", admin.site.urls),
    ]

3. Add "django_db_translate.middleware.DBTranslateAdminMiddleware" to your MIDDLEWARE setting after any other Locale manipulating middlewares::

    MIDDLEWARE = [
        ...,
        'django_db_translate.middleware.DBTranslateAdminMiddleware'
    ]

4. Give the ``Dbtranslate | db translate permissions | Manage translations`` permission to any user that requires translation editing permissions

