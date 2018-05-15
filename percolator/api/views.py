from apistar import types, validators
from ..search import BaseTagger, SpeciesQueryIndexer
from elasticsearch import Elasticsearch

from percolator.conf import settings


class SpeciesExtractionParams(types.Type):
    """
    Validator for `extract_endpoint` endpoint request data.
    """
    content = validators.String(
        max_length=1024 * 1024 * 10,
        description='Text to be analyzed for species mentions'
    )
    offset = validators.Integer(
        minimum=0, allow_null=True, description='The paging offset'
    )
    limit = validators.Integer(
        minimum=1, default=10, allow_null=True, description='The paging limit'
    )
    min_score = validators.Number(
        minimum=0.1,
        allow_null=True,
        description='The minimum search score required. No default is applied when not provided. '
        'Ignored when `constant_score` is on.',
    )
    constant_score = validators.Boolean(
        default=True,
        allow_null=True,
        description='Disables relevance scoring. The response will only include the species names',
    )


def extract_species(query: SpeciesExtractionParams, es_client: Elasticsearch) -> dict:
    """
    Extracts species mentions in the supplied text `content`.

    Response: a list of species names or, if `constant_score` is `False`,
    a mapping of species names to relevance scores.
    """
    indexer = SpeciesQueryIndexer(client=es_client, index=settings.ELASTICSEARCH_INDEX)
    tagger = BaseTagger(indexer=indexer)
    tags = tagger.get_tags(
        content=query.content,
        min_score=query.min_score,
        constant_score=query.constant_score,
        offset=query.offset,
        limit=query.limit,
    )

    return tags
