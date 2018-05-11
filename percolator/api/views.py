from apistar import http
from ..search import BaseTagger, SpeciesQueryIndexer
from elasticsearch import Elasticsearch


def tag(
    data: http.RequestData,
    offset: http.QueryParam,
    limit: http.QueryParam,
    min_score: http.QueryParam,
    es_client: Elasticsearch
) -> dict:
    tagger = BaseTagger(indexer=SpeciesQueryIndexer(client=es_client))
    tags = tagger.get_tags(
        content=data.get('content'),
        min_score=min_score, offset=offset, limit=limit
    )
    response = {t[0]: t[1] for t in tags}
    return response
