from django.db import models


class DBTranslatePermissions(models.Model):
    """Unmanaged model to insert translation permissions."""
    class Meta:
        managed = False
        default_permissions = ()
        permissions = [
            ("manage_translations", "Manage translations"),
            ("administrate_translations", "Translation Administrator")
        ]
