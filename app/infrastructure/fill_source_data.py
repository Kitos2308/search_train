import csv
from datetime import datetime

from sqlalchemy.dialects.postgresql import insert

from app.core.models import ExampleText
from app.infrastructure.database import Database


async def bulk_insert_data(data: list[dict]) -> None:
    statement = insert(ExampleText).values(data)
    statement = statement.on_conflict_do_nothing()
    async with Database.session() as session:
        await session.execute(statement)
        await session.commit()


def mapper_data():
    with open("utils/source_data.csv", newline="") as csvfile:
        spamreader = csv.reader(csvfile)
        return [
            {
                "entity_id": int(row[1]),
                "type": row[2],
                "source_txt1": row[3],
                "source_txt2": row[4],
                "source_txt3": row[5],
                "source_txt4": row[6],
                "img": row[7],
                "entity_date": datetime.strptime(row[8], "%Y-%m-%d %H:%M:%S.%f %z"),
            }
            for index, row in enumerate(spamreader)
            if index != 0
        ]
