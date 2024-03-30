from trytond.model import fields


class Vector(fields.Field):
    _type = 'vector'
    _sql_type = 'VECTOR'
