import json

from trytond.model import fields


class Vector(fields.Field):
    _type = 'vector'
    _py_type = list

    def __init__(self, string='', size=None, help='', required=False,
            readonly=False, domain=None, states=None, on_change=None,
            on_change_with=None, depends=None, context=None,
            loading='eager'):
        super().__init__(string=string, help=help, required=required,
            readonly=readonly, domain=domain, states=states,
            on_change=on_change, on_change_with=on_change_with,
            depends=depends, context=context, loading=loading)
        self.size = size

    @property
    def _sql_type(self):
        if isinstance(self.size, int):
            return 'vector(%s)' % self.size
        else:
            return 'vector'

    def __get__(self, inst, cls):
        value = super().__get__(inst, cls)
        if isinstance(value, str) and value.startswith('[') and value.endswith(']'):
            return json.loads(value) # This way we return a list, not a string
        return value
