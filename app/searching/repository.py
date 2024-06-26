from typing import Any
from elasticsearch import AsyncElasticsearch
from elasticsearch_dsl import AsyncSearch
from elasticsearch_dsl.query import (
    Bool,
    ConstantScore,
    DisMax,
    FunctionScore,
    Term,
    MatchPhrase,
    Match
)


SEARCH_INDEX_NAME_ALPHA = "searchable-document-index-alpha"
SEARCH_INDEX_NAME_BETA = "searchable-document-index-beta"
ACTIVE_SEARCH_INDEX_ALIAS = "searchable-document-index-alias"

class SearchingRepository:
    elasticsearch_connection: AsyncElasticsearch

    def __init__(self, using: AsyncElasticsearch) -> None:
        self.elasticsearch_connection = using

    async def search(
            self,
            query: str,

    ) -> Any:
        search = construct_search(query, self.elasticsearch_connection, SEARCH_INDEX_NAME_ALPHA)
        search_response = await search.execute()
        f= search_response



def construct_search(
        query: str,
        using: AsyncElasticsearch,
        index:str,
        is_sort_by_date: bool = False
) -> AsyncSearch:
    return (AsyncSearch(
        using=using,
        index=index,
    ).query(
        FunctionScore(
            query=Bool(
                should=[
                    get_wide_relevancy(query),
                    # Bool(
                    #     should=[
                    #         Term(
                    #             type={
                    #                 "value": 'article',
                    #                 "boost": 100500,  # does not matter which number, as long as it's high
                    #             }
                    #         ),
                    #     ],
                    # ),
                ]
            ),
            field_value_factor={
                "field": "rating",
                "modifier": "ln2p",
                "missing": 1,
            },
        )
    ).suggest(
        "spellcheck",
        query,
        phrase={
            "field": "primary_field.trigram",
            "size": 1,
            "gram_size": 3,
            "direct_generator": [{"field": "primary_field.trigram"}],
            "collate": {
                "query": {
                    "source": {"match_phrase": {"primary_field": "{{suggestion}}"}}
                },

            },
        },
    ).highlight('primary_field', fragment_size=100,pre_tags=["<bold>"], post_tags=["</bold>"], phrase_limit=1))


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

    # minimal_criteria = MatchPhrase(
    #     common_field={
    #         "query": query_string,
    #         "minimum_should_match": -1,
    #         "zero_terms_query": "all",
    #     },
    # )

    return Bool(
        should=[
            DisMax(
                queries=[
                    *wide_relevancy_signals,
                ]
            ),
        ],
        # filter=minimal_criteria,
    )


