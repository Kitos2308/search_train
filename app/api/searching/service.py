from dataclasses import dataclass

from app.core.searching.repository import SearchingRepository


@dataclass
class SearchingService:
    repository: SearchingRepository

    async def get_most_relevant_result(
            self,
            query: str
    ) -> None:
        return await self.repository.search(query)
