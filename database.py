# This file is part widgets module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import logging

from pgvector.psycopg import register_vector
from psycopg import ProgrammingError

logger = logging.getLogger(__name__)


class DatabaseMixin:

    @classmethod
    def create(cls, connection, database_name):
        super().create(connection, database_name)

        database = cls(database_name)
        with database.get_connection() as db_connection:
            cursor = db_connection.cursor()
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")

    def get_connection(
            self, autocommit=False, readonly=False, statement_timeout=None):
        conn = super().get_connection(
            autocommit=autocommit, readonly=readonly,
            statement_timeout=statement_timeout)
        try:
            register_vector(conn)
        except ProgrammingError as exc:
            logger.warning(
                'Failed to register pgvector type, '
                'pgvector extension may not be installed: "%s"', exc)
        return conn
