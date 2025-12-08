from functools import update_wrapper
from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.urls import reverse, reverse_lazy

from django_db_translate.admin.views import locale_view
from django_db_translate.translations import registry


class DBTranslateAdmin(admin.AdminSite):
    translation_section_label = "Translations"

    def get_urls(self):
        urls = super().get_urls()

        def wrap(view, cacheable=False):
            def wrapper(*args, **kwargs):
                return self.admin_view(view, cacheable)(*args, **kwargs)

            wrapper.admin_site = self  # pyright: ignore
            # Used by LoginRequiredMiddleware.
            wrapper.login_url = reverse_lazy("admin:login", current_app=self.name)  # pyright: ignore
            return update_wrapper(wrapper, view)

        custom_urls = [
            path(
                "dbtranslate/",
                wrap(self.app_index),
                kwargs={"app_label": "dbtranslate"},
                name="dbtranslate_list"
            )
        ]
        for locale, lobj in registry.registry.items():
            custom_urls.append(
                path(
                    lobj.admin_url,
                    self.admin_view(locale_view),
                    kwargs={"locale": lobj, "context_func": self.each_context},
                    name=f"locale_view_{locale}"
                )
            )
        return custom_urls + urls

    def get_app_list(self, request, app_label=None):
        app_list = super().get_app_list(request, app_label=app_label)

        if (
            app_label is None or
            app_label == 'dbtranslate'
        ) and request.user.has_perm("dbtranslate.manage_translations"):
            section = next(
                (a for a in app_list if a["name"] == self.translation_section_label),
                None
            )

            if not section:
                section = {
                    "name": self.translation_section_label,
                    "app_label": "dbtranslate",
                    "models": [],
                    "app_url": reverse(
                        "admin:dbtranslate_list",
                        current_app=self.name
                    ),
                    # "app_url": None,
                    "has_module_perms": True,
                    "perms": {"change": True},
                }
                app_list.append(section)

            for locale, lobj in sorted(registry.registry.items(), key=lambda x: x[1].fullname.lower()):
                section["models"].append({
                    "name": lobj.fullname,
                    "object_name": locale,
                    "admin_url": reverse(f"admin:locale_view_{locale}"),
                    "view_only": True,
                    "perms": {"change": True},
                })

        return app_list
