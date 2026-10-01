# This file is part widgets module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from .database import DatabaseMixin

__all__ = ['register', 'routes', 'DatabaseMixin', 'FernetEncryptionMixin']


def __getattr__(name):
    if name == 'FernetEncryptionMixin':
        from .encryption import FernetEncryptionMixin
        globals()[name] = FernetEncryptionMixin
        return FernetEncryptionMixin
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')


def register():
    from trytond.pool import Pool
    from . import ir, routes

    globals()['routes'] = routes

    Pool.register(
        ir.View,
        module='widgets', type_='model')
