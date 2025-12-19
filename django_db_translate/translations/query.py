from itertools import chain
from typing import Iterable, Optional

from django.db import models

DBTranslationString = str | tuple[str, str]


class DBStringPO:

    def __init__(self, string: str, context: Optional[str] = None, comment: Optional[str] = None):
        self.string = string
        self.context = context
        self.comment = comment

    def translation_strings(self) -> list[str]:
        tm = []
        if self.comment:
            tm.append("# Translators: %s" % self.comment)

        if self.context:
            tm.append("pgettext(%r, %r)" % (self.context, self.string))
        else:
            tm.append("gettext(%r)" % self.string)

        return tm


class DBTranslateQueryManager:

    def __init__(self, model: models.Model, fields: Iterable[str]):
        self.model = model
        self.fields = fields

    def get_strings(self) -> list[DBStringPO]:
        db_strings = [
            DBStringPO(s)
            for s in chain.from_iterable(self.model.objects.values_list(*self.fields).distinct())
            if s
        ]
        return db_strings
