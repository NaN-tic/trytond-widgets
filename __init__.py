# This file is part widgets module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import ir
from . import routes
from . import tools

__all__ = ['register', 'routes', 'tools']

def register():
    Pool.register(
        ir.View,
        module='widgets', type_='model')
