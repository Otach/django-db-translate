from itertools import chain
from typing import Iterable
from django.db import models

DBTranslationString = str | tuple[str, str]


class DBTranslateQueryManager:

    def __init__(self, model: models.Model, fields: Iterable[str]):
        self.model = model
        self.fields = fields

    def _get_strings(self) -> list[DBTranslationString]:
        strings = self.get_strings()
        strings = self.filter(strings)
        return self.sort(strings)

    def get_strings(self) -> list[DBTranslationString]:
        db_strings = set(
            chain.from_iterable(
                self.model.objects.values_list(*self.fields).distinct()
            )
        )
        return db_strings

    def filter(self, strings: list[DBTranslationString]) -> list[DBTranslationString]:
        # Override in subclass
        return strings

    def sort(self, strings: list[DBTranslationString]) -> list[DBTranslationString]:
        # Override in subclass
        return strings
