from django.conf import settings
from django.urls import reverse
from django.utils.translation import activate


class DBTranslateAdminMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith(reverse('admin:index')):
            activate(settings.LANGUAGE_CODE)

        return self.get_response(request)
