from apistar import types, validators
from ..search import BaseTagger, SpeciesQueryIndexer
from elasticsearch import Elasticsearch

from percolator.conf import settings


class TagQuery(types.Type):
    """
    Validator for `tag` endpoint request data.
    """
    content = validators.String(max_length=1024 * 1024 * 10)
    offset = validators.Integer(minimum=0, allow_null=True)
    limit = validators.Integer(minimum=1, allow_null=True)
    min_score = validators.Number(minimum=0.1, allow_null=True)
    constant_score = validators.Boolean(default=True, allow_null=True)


def tag(
    query: TagQuery,
    es_client: Elasticsearch
) -> dict:
    indexer = SpeciesQueryIndexer(client=es_client, index=settings.ELASTICSEARCH_INDEX)
    tagger = BaseTagger(indexer=indexer)
    tags = tagger.get_tags(
        content=query.content,
        min_score=query.min_score, constant_score=query.constant_score,
        offset=query.offset, limit=query.limit
    )

    return tags
