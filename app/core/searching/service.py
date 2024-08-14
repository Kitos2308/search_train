from dataclasses import dataclass
from typing import Any

from app.core.searching.repository import SearchingRepository


@dataclass
class SearchingService:
    repository: SearchingRepository

    async def get_most_relevant_result(
            self,
            query: str
    ) -> Any:
        return await self.repository.search(query)
