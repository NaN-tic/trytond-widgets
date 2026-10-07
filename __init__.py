# This file is part widgets module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

__all__ = ['register', 'routes']

def register():
    # Defer imports until registration to avoid the circular import through
    # routes: cannot import name 'app' from partially initialized trytond.wsgi.
    from trytond.pool import Pool
    from . import ir
    from . import routes

    globals()['routes'] = routes

    Pool.register(
        ir.View,
        module='widgets', type_='model')
