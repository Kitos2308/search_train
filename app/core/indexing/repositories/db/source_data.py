from app.infrastructure.database import Database
from .sql_source_query import source_first_example
from app.infrastructure.schemas.source_example_one import TextOne, SearchableEntity


async def get_source_data() -> list[SearchableEntity]:
    async with Database.session() as session:
        result = await session.execute(source_first_example)
        source_data = result.fetchall()
        return [TextOne.model_validate(data) for data in source_data]