from django.db import models


class DBTranslatePermissions(models.Model):
    """Unmanaged model to insert translation permissions."""
    class Meta:
        managed = False
        permissions = [
            ("manage_translations", "Manage translations")
        ]
