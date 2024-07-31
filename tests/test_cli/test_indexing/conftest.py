from typing import Any


class CursorMock:
    def __init__(self, rows):
        self.rows = rows
        self.rowcount = len(rows)

    def __aiter__(self):
        yield iter(self.rows)

    def __iter__(self):
        return iter(self.rows)

    def fetchall(self):
        return self.mock_param()

    def mock_param(self):
        return self.rows
