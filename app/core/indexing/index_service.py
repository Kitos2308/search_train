from dataclasses import dataclass
from app.core.indexing.repositories.db.source_data import get_source_data
from app.infrastructure.schemas.source_example_one import SearchableEntity
from app.core.indexing.index_repository import convert_entities_to_index_documents, IndexingRepository


@dataclass
class IndexingService:
    repository: IndexingRepository

    async def _get_searchable_entity(
            self,

    ) -> list[SearchableEntity]:
        return await get_source_data()

    async def chunked_add_documents(
            self,
            write_index: str,
    ) -> None:
        searchable_entities = await self._get_searchable_entity()

        documents = convert_entities_to_index_documents(searchable_entities)
        await self.repository.add_documents(documents, write_index=write_index)
