import math

from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

# from app.core.indexing.constants import RepresentationTypeEnum
# from app.core.indexing.dto import (
#     ArtDTO,
#     CollectionDTO,
#     GenreDTO,
#     PersonDTO,
#     PublisherDTO,
#     RatingModel,
#     SearchableEntity,
#     SeriesDTO,
#     TagDTO,
# )
# from app.infrastructure.index_mapping import IndexDocument


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
        if isinstance(entity, ArtDTO):
            document = turn_art_into_index_document(entity)
        elif isinstance(entity, PersonDTO):
            document = turn_person_into_index_document(entity)
        elif isinstance(entity, CollectionDTO):
            document = turn_collection_into_index_document(entity)
        elif isinstance(entity, SeriesDTO):
            document = turn_series_into_index_document(entity)
        elif isinstance(entity, GenreDTO):
            document = turn_genre_into_index_document(entity)
        elif isinstance(entity, TagDTO):
            document = turn_tag_into_index_document(entity)
        elif isinstance(entity, PublisherDTO):
            document = turn_publisher_into_index_document(entity)
        else:
            raise ValueError(f"unknown type {type(entity)}")
        index_documents.append(document)
    return index_documents


def turn_art_into_index_document(art: ArtDTO) -> IndexDocument:
    document = IndexDocument(
        primary_field=art.title.strip(),
        secondary_field=" ".join((art.persons, art.genre_names)).strip(),
        database_id=art.id,
        uuid=art.uuid,
        representation_type=art.representation_type,
        face_ids=art.face_ids,
        genre_ids=art.genre_ids,
        library_ids=art.library_ids,
        language=art.language,
        first_time_sale_at=art.first_time_sale_at,
        rating=_compute_document_rating(art),
        isbn=art.isbn.split(", ") if art.isbn else None,
        disallowed_country_codes=art.disallowed_country_codes,
        novelty_rating=art.novelty_rating,
    )
    document.meta.id = _generate_predictable_id(
        entity_type="art", entity_database_id=art.id
    )
    return document


def turn_person_into_index_document(person: PersonDTO) -> IndexDocument:
    document = IndexDocument(
        primary_field=person.full_name,
        database_id=person.id,
        representation_type=RepresentationTypeEnum.person.value,
        rating=_compute_document_rating(person),
        face_ids=person.face_ids,
    )
    document.meta.id = _generate_predictable_id(
        entity_type="person", entity_database_id=person.id
    )
    return document


def turn_collection_into_index_document(collection: CollectionDTO) -> IndexDocument:
    document = IndexDocument(
        primary_field=collection.title.strip(),
        database_id=collection.id,
        representation_type=RepresentationTypeEnum.collection.value,
        rating=5,
        face_ids=collection.face_ids,
    )
    document.meta.id = _generate_predictable_id(
        entity_type="collection", entity_database_id=collection.id
    )
    return document


def turn_series_into_index_document(series: SeriesDTO) -> IndexDocument:
    document = IndexDocument(
        primary_field=series.title.strip(),
        secondary_field=series.persons or "",
        database_id=series.id,
        representation_type=RepresentationTypeEnum.series.value,
        rating=5,
        face_ids=series.face_ids,
    )
    document.meta.id = _generate_predictable_id(
        entity_type="series", entity_database_id=series.id
    )
    return document


def turn_genre_into_index_document(genre: GenreDTO) -> IndexDocument:
    document = IndexDocument(
        primary_field=genre.title.strip(),
        database_id=genre.id,
        representation_type=RepresentationTypeEnum.genre.value,
        rating=_compute_document_rating(genre),
        face_ids=genre.face_ids,
    )
    document.meta.id = _generate_predictable_id(
        entity_type="genre", entity_database_id=genre.id
    )
    return document


def turn_tag_into_index_document(tag: TagDTO) -> IndexDocument:
    document = IndexDocument(
        primary_field=tag.title.strip(),
        database_id=tag.id,
        representation_type=RepresentationTypeEnum.tag.value,
        rating=_compute_document_rating(tag),
        face_ids=tag.face_ids,
    )
    document.meta.id = _generate_predictable_id(
        entity_type="tag", entity_database_id=tag.id
    )
    return document


def turn_publisher_into_index_document(publisher: PublisherDTO) -> IndexDocument:
    document = IndexDocument(
        primary_field=publisher.title.strip(),
        database_id=publisher.id,
        rating=5,
        representation_type=RepresentationTypeEnum.publisher.value,
        face_ids=publisher.face_ids,
    )
    document.meta.id = _generate_predictable_id(
        entity_type="publisher", entity_database_id=publisher.id
    )
    return document


def _generate_predictable_id(entity_type: str, entity_database_id: int) -> str:
    return f"{entity_type}-{entity_database_id}"


def _compute_document_rating(model: RatingModel) -> float:
    return math.log(model.rating + 2)
