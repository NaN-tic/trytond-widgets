from trytond.model import fields
import numpy as np


class Vector(fields.Field):
    _type = 'vector'
    _sql_type = 'VECTOR'
    _py_type = np.ndarray
