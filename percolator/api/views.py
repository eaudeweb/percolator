import requests
from uuid import uuid4
from typing import Union
from apistar import types, validators, http
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


def get_species(es_client, content, min_score=None, constant_score=True, offset=None, limit=None):
    indexer = SpeciesQueryIndexer(client=es_client, index=settings.ELASTICSEARCH_INDEX)
    tagger = BaseTagger(indexer=indexer)
    species = tagger.get_tags(
        content=content,
        min_score=min_score,
        constant_score=constant_score,
        offset=offset,
        limit=limit
    )

    return species


def extract_species(query: SpeciesExtractionParams, es_client: Elasticsearch) -> dict:
    """
    Extracts species mentions in the supplied text `content`.

    Response: a list of species names or, if `constant_score` is `False`,
    a mapping of species names to relevance scores.
    """
    return get_species(
        es_client=es_client,
        content=query.content,
        min_score=query.min_score,
        constant_score=query.constant_score,
        offset=query.offset,
        limit=query.limit
    )


def extract_species_from_file(request: http.Request, es_client: Elasticsearch) -> Union[http.Response, dict]:
    headers = {
        'Accept': 'application/json',
        'Content-Disposition': f'attachment; filename={uuid4()}',
    }
    try:
        response = requests.put(
            f'{settings.TIKA_URL}/rmeta/text',
            data=request.body, headers=headers,
            verify=False, timeout=settings.TIKA_TIMEOUT
        )
    except requests.exceptions.Timeout:
        return http.Response({'error': 'text extraction timed out'}, status_code=500)
    tika_data = response.json()
    text_content = tika_data[0]['X-TIKA:content'].strip()
    species = get_species(es_client=es_client, content=text_content)
    return species
