from .loader import TranslationRegistry, EntryKeyIdentifier

registry = TranslationRegistry()

__all__ = [
    'registry',
    'EntryKeyIdentifier'
]
