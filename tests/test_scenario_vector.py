import unittest

from pgvector.vector import Vector as PgVector

from trytond.modules.widgets.vector import Vector
from trytond.tests.test_tryton import DB_NAME, drop_db
from trytond.tests.tools import activate_modules
from trytond.transaction import Transaction


class TestVector(unittest.TestCase):

    def setUp(self):
        drop_db()
        super().setUp()

    def tearDown(self):
        drop_db()
        super().tearDown()

    def test(self):
        activate_modules('widgets')

        with Transaction().start(DB_NAME, 1):
            field = Vector('Embedding', size=2)
            values = field.get([1], None, 'embedding', [{
                    'id': 1,
                    'embedding': PgVector([1.0, 2.0]),
                    }])

            self.assertEqual(values[1], [1.0, 2.0])
            self.assertEqual(len(values[1]), 2)
