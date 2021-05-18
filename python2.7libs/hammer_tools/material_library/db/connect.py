import os
import sqlite3

from .configs import DB_FILE_PATH
from .create import createDatabase


class RowFactory(sqlite3.Row):
    def get(self, key, default=None):
        try:
            return self[key]
        except (KeyError, IndexError):
            return default


def connect():
    if not os.path.exists(DB_FILE_PATH):
        createDatabase(DB_FILE_PATH)

    connection = sqlite3.connect(DB_FILE_PATH,
                                 detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    connection.row_factory = RowFactory
    return connection
