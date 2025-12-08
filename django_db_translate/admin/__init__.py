from .admin import DBTranslateAdmin
from django.contrib.admin import site as _site

site = DBTranslateAdmin()
