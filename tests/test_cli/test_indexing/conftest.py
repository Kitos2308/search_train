from typing import Any


class CursorMock:
    def __init__(self, rows):
        self.rows = rows
        self.rowcount = len(rows)

    def __aiter__(self):
        yield iter(self.rows)

    def __iter__(self):
        return iter(self.rows)

    @property
    def fetchall(self):
        return param

def param():
    return {'suka':'suka'}

class RowMock:
    def __init__(self, result: dict[str, Any]):
        self.result = result

    @property
    def fetchall(self):
        return self.result.items()
