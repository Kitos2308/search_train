from typing import Any

from elasticsearch import AsyncElasticsearch
from elasticsearch_dsl import AsyncSearch
from elasticsearch_dsl.query import (
    Bool,
    ConstantScore,
    DisMax,
    FunctionScore,
    MatchPhrase,
)

from app.settings import settings


class SearchingRepository:
    elasticsearch_connection: AsyncElasticsearch

    def __init__(self, using: AsyncElasticsearch) -> None:
        self.elasticsearch_connection = using

    async def search(
        self,
        query: str,
    ) -> Any:
        search = construct_search(query, self.elasticsearch_connection, settings.SEARCH_INDEX_NAME_ALPHA)
        return await search.execute()


def construct_search(
    query: str,
    using: AsyncElasticsearch,
    index: str,
) -> AsyncSearch:
    return (
        AsyncSearch(
            using=using,
            index=index,
        )
        .query(
            FunctionScore(
                query=Bool(
                    should=[
                        get_wide_relevancy(query),
                    ],
                ),
                field_value_factor={
                    "field": "rating",
                    "modifier": "ln2p",
                    "missing": 1,
                },
            ),
        )
        .suggest(
            "spellcheck",
            query,
            phrase={
                "field": "primary_field.trigram",
                "size": 1,
                "gram_size": 3,
                "direct_generator": [{"field": "primary_field.trigram"}],
                "collate": {
                    "query": {"source": {"match_phrase": {"primary_field": "{{suggestion}}"}}},
                },
            },
        )
        .highlight(
            "primary_field",
            fragment_size=100,
            pre_tags=["<bold>"],
            post_tags=["</bold>"],
            phrase_limit=1,
        )
    )


def get_wide_relevancy(query_string: str):
    wide_relevancy_signals = [
        ConstantScore(
            filter=MatchPhrase(primary_field={"query": query_string}),
            boost=10,
        ),
        ConstantScore(
            filter=MatchPhrase(secondary_field={"query": query_string}),
            boost=10,
        ),
    ]
    return Bool(
        should=[
            DisMax(
                queries=[
                    *wide_relevancy_signals,
                ],
            ),
        ],
    )
