from dataclasses import dataclass
from search.core.crud.source_data import get_source_data
from search.core.schemas.source_example_one import SearchableEntity
from search.index_repository import convert_entities_to_index_documents, IndexingRepository

@dataclass
class IndexingService:
    repository: IndexingRepository

    async def _get_searchable_entity(
            self,

    ) -> list[SearchableEntity]:
        return await get_source_data()

    # async def reindex_all_searchable_entities(
    #         self, chunk_size: int, write_index: str
    # ) -> None:
    #     await asyncio.gather(
    #         *[
    #             self.chunked_add_documents(
    #                 entity_type,
    #                 chunk_size=chunk_size,
    #                 from_sql=True,
    #                 write_index=write_index,
    #             )
    #             for entity_type in list(SearchableEntityType)
    #         ]
    #     )

    async def chunked_add_documents(
            self,
            write_index: str,
    ) -> None:
        searchable_entities = await self._get_searchable_entity()

        documents = convert_entities_to_index_documents(searchable_entities)
        await self.repository.add_documents(documents, write_index=write_index)
