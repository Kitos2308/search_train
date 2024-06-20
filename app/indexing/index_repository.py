from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from app.core.schemas.source_example_one import SearchableEntity, TextOne
from app.indexing.index_mapper import IndexDocument


class IndexingRepository:
    elasticsearch_connection: AsyncElasticsearch

    def __init__(self, using: AsyncElasticsearch) -> None:
        self.elasticsearch_connection = using

    async def add_documents(
            self, documents: list[IndexDocument], write_index: str
    ) -> None:
        document_payload = self._prepare_document_payload(documents, write_index)
        await async_bulk(self.elasticsearch_connection, document_payload, max_retries=5)

    @classmethod
    def _prepare_document_payload(
            cls, documents: list[IndexDocument], write_index: str
    ) -> list[dict]:
        cls._set_index(documents, write_index)
        document_payload = [
            document.to_dict(include_meta=True) for document in documents
        ]
        return document_payload

    @staticmethod
    def _set_index(documents: list[IndexDocument], write_index: str) -> None:
        for document in documents:
            document._index._name = write_index


def convert_entities_to_index_documents(
        entities: list[SearchableEntity],
) -> list[IndexDocument]:
    index_documents = []
    for entity in entities:
        if isinstance(entity, TextOne):
            document = turn_example_text_into_index_document(entity)
        else:
            raise ValueError(f"unknown type {type(entity)}")
        index_documents.append(document)
    return index_documents


def turn_example_text_into_index_document(example_text: TextOne) -> IndexDocument:
    document = IndexDocument(
        primary_field=example_text.text,
        img=example_text.img,
        entity_date=example_text.entity_date,
        type=example_text.type
    )
    document.meta.id = example_text.meta_id
    return document
