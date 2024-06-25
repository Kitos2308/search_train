from dynaconf import settings
from elasticsearch import AsyncElasticsearch
from elasticsearch_dsl import (
    Date,
    Float,
    Integer,
    Keyword,
    Long,
    MetaField,
    Text,
    analyzer,
)
from loguru import logger

from elasticsearch_dsl import AsyncDocument

from app.numerals import POPULAR_NUMERALS, FROM_0_TO_1000

SEARCH_INDEX_NAME_ALPHA = "searchable-document-index-alpha"
SEARCH_INDEX_NAME_BETA = "searchable-document-index-beta"
ACTIVE_SEARCH_INDEX_ALIAS = "searchable-document-index-alias"

GARBAGE_TOKENS = [
    "с иллюстрациями",
    "скачать бесплатно",
    "электронная книга",
    "читать бесплатно",
    "читать онлайн",
    "epub",
    "епаб",
    "купить",
    "автор",
]


class IndexDocument(AsyncDocument):
    primary_field = Text(
        analyzer=analyzer(
            "primary_field_analyzer",
            tokenizer="standard",
            char_filter=[
                "html_strip",
                "garbage_tokens_strip",
                "similar_sounds",
            ],
            filter=[
                "lowercase",
                "numerals",
                "russian_stop",
                "russian_stemmer",
            ],
        ),
        fields={
            "precise_match": {"type": "text", "analyzer": "precise_match_analyzer"},
            "precise_match_no_special_symbols": {
                "type": "text",
                "analyzer": "precise_match_no_special_symbols_analyzer",
            },
            "trigram": {"type": "text", "analyzer": "trigram"},
            "reverse": {"type": "text", "analyzer": "reverse"},
            "keyword": {"type": "text", "analyzer": "keyword"},
            "autocomplete": {"type": "text", "analyzer": "autocomplete_analyzer"},
        },
        copy_to="common_field",
    )
    secondary_field = Text(
        analyzer=analyzer(
            "secondary_field_analyzer",
            tokenizer="standard",
            char_filter=[
                "html_strip",
                "garbage_tokens_strip",
                "similar_sounds",
            ],
            filter=[
                "lowercase",
                "numerals",
                "russian_stop",
                "russian_stemmer",
            ],
        ),
        fields={
            "precise_match": {"type": "text", "analyzer": "precise_match_analyzer"},
            "precise_match_no_special_symbols": {
                "type": "text",
                "analyzer": "precise_match_no_special_symbols_analyzer",
            },
            "autocomplete": {"type": "text", "analyzer": "autocomplete_analyzer"},
        },
        copy_to="common_field",
    )

    common_field = Text(
        analyzer=analyzer(
            "common_field_analyzer",
            tokenizer="standard",
            char_filter=["html_strip", "garbage_tokens_strip", "similar_sounds"],
            filter=["lowercase", "numerals", "russian_stop", "russian_stemmer"],
        ),
    )

    img = Keyword()
    entity_date = Date()
    type = Keyword()

    @classmethod
    async def initialize(
            cls, target_index: str, using: AsyncElasticsearch = None
    ) -> None:
        """
        Create the index and populate the mappings if the index does not exist.

        Same as Document.init, but if the index already exists, the method skips the mapping update
        """
        new_index = cls._index.clone(name=target_index)
        if not await new_index.exists(using=using):
            logger.info("index doesn't exist, create it")
            await new_index.create(using=using)
            cls._index = new_index
        else:
            logger.info("index already exists, skip the creation")

    class Index:
        name = (
            ACTIVE_SEARCH_INDEX_ALIAS
        )  # put alias here, so we read only from it
        dynamic = MetaField("strict")
        settings = {
            "index": {
                "analysis": {
                    "analyzer": {
                        "trigram": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "shingle"],
                        },
                        "autocomplete_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "char_filter": ["similar_sounds"],
                            "filter": [
                                "lowercase",
                                "numerals",
                                "custom_synonyms",
                                "autocomplete_ten",
                            ],
                        },
                        "reverse": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "reverse"],
                        },
                        "precise_match_analyzer": {
                            "type": "custom",
                            "tokenizer": "whitespace",
                            "char_filter": ["similar_sounds"],
                            "filter": ["lowercase", "numerals", "custom_synonyms"],
                        },
                        "precise_match_no_special_symbols_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "char_filter": ["similar_sounds"],
                            "filter": ["lowercase", "numerals", "min_length_is_2"],
                        },
                    },
                    "char_filter": {
                        # Лучше применять до similar_sounds, который заставит
                        # коверкать слова: например, вместо "электронная" придется написать "електронная".
                        "garbage_tokens_strip": {
                            "type": "mapping",
                            "mappings": [
                                f"{garbage_token} => "
                                for garbage_token in GARBAGE_TOKENS
                            ],
                        },
                        # При применении, similar_sounds будут влиять на всё: стемминг,
                        # стоп-слова, другие char_filters, следующие после них
                        "similar_sounds": {
                            "type": "mapping",
                            "mappings": [
                                "ё => е",
                                "Ё => е",
                                "э => е",
                                "Э => е",
                                "ъ => ь",
                                "Ъ => ь",
                                "уи => ви",
                                "Уи => ви",
                                "уИ => ви",
                                "УИ => ви",
                            ],
                        },
                    },
                    "filter": {
                        "shingle": {
                            "type": "shingle",
                            "min_shingle_size": 2,
                            "max_shingle_size": 3,
                        },
                        "autocomplete_ten": {
                            "type": "edge_ngram",
                            "min_gram": 3,
                            "max_gram": 10,
                        },
                        "custom_synonyms": {
                            "type": "synonym",
                            "synonyms": [
                                "с++ => c++",
                                "с# => c#",
                            ],
                        },
                        "min_length_is_2": {
                            "type": "length",
                            "min": 2,
                        },
                        "numerals": {
                            "type": "synonym",
                            "synonyms": POPULAR_NUMERALS,
                        },
                        "russian_stemmer": {
                            "type": "stemmer",
                            "language": "russian",
                        },
                        "russian_stop": {"type": "stop", "stopwords": "_russian_"},
                    },
                }
            }
        }
