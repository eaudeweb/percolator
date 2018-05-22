from apistar import validators
from apistar.http import Response
from apistar.exceptions import BadRequest
from elasticsearch import Elasticsearch

from percolator.conf import settings
from ..search import TAG_DOMAINS
from .components import MultiPartForm
from ..core.types import CoercingType
from ..core.text import extract_text
from ..core.exceptions import TextExtractionError, TextExtractionTimeout


def list_tag_domains() -> dict:
    """
    Lists tag domains.

    Returns:
        dict mapping domain names to their descriptions.
    """
    return {k: v.description for k, v in TAG_DOMAINS.items()}


class DomainValidator(validators.String):
    """Custom string validator for domains"""
    errors = {'exact': 'Unknown domain'}


class ExtractionJSONParams(CoercingType):
    """Validator for tag extraction request data."""

    domains = validators.Array(
        items=DomainValidator(enum=list(TAG_DOMAINS.keys())),
        description='List of domains to search, if not provided ALL domains will be included',
        allow_null=True,
    )
    content = validators.String(
        max_length=1024 * 1024 * 10,
        default='',
        allow_null=True,
        description='Text to be analyzed for species mentions'
    )
    offset = validators.Integer(
        minimum=0, allow_null=True, description='The paging offset'
    )
    limit = validators.Integer(
        minimum=1,
        maximum=10000,
        default=10,
        allow_null=True,
        description='The paging limit.',
    )
    min_score = validators.Number(
        minimum=0.1,
        allow_null=True,
        description='The minimum search score required. No default is applied when not provided. '
        'Ignored when `constant_score` is on.',
    )
    constant_score = validators.Boolean(
        default=True,
        allow_null=False,
        description='Disables relevance scoring when `True`. All results will have score `1`.',
    )


def get_domain_tags(
    domain,
    es_client,
    content,
    min_score=None,
    constant_score=True,
    offset=None,
    limit=None,
):
    """Fetches tags for a domain"""
    tag_domain = TAG_DOMAINS[domain]
    indexer = tag_domain.query_indexer(
        client=es_client, index=settings.ELASTICSEARCH_INDEX
    )
    tagger = tag_domain.tagger(indexer=indexer)
    return tagger.get_tags(
        content=content,
        min_score=min_score,
        constant_score=constant_score,
        offset=offset,
        limit=limit,
    )


def extract_from_json(params: ExtractionJSONParams, es_client: Elasticsearch) -> dict:
    """Tag extraction endpoint handler, accepts parameters as JSON."""
    if not params.content:
        raise BadRequest({'content': 'Required and not provided'})

    domains = params.domains or TAG_DOMAINS.keys()
    response = {}
    for domain in domains:
        response[domain] = get_domain_tags(
            domain=domain,
            es_client=es_client,
            content=params.content,
            min_score=params.min_score,
            constant_score=bool(params.constant_score),
            offset=params.offset,
            limit=params.limit,
        )
    return response


def extract_from_form(form_data: MultiPartForm, es_client: Elasticsearch) -> dict:
    """
    Tag extraction endpoint handler, accepting a multi-part form.

    Form fields must conform to `ExtractionJSONParams` attributes, plus a `file` field.
    """
    params = dict(form_data)  # Convert from ImmutableDict
    params = {k: v[0] for k, v in params.items()}  # Strip array wrappers from fields
    try:
        file = params.pop('file')
    except KeyError:
        raise BadRequest({'file': 'Required and not provided'})

    params['domains'] = [
        d.strip() for d in params.get('domains', '').split(',')
    ] or None
    params.pop('content', None)  # Ignore `content`, will be populated from file's text.

    try:
        params = ExtractionJSONParams.validate(params, allow_coerce=True)
    except validators.ValidationError as exc:
        raise BadRequest(exc.detail)

    try:
        params.content = extract_text(file.stream)
    except TextExtractionTimeout:
        return Response('Text extraction timed out', status_code=500)

    except TextExtractionError:
        return Response('Text extraction could not be performed', status_code=500)

    domains = params.domains or TAG_DOMAINS.keys()
    response = {}
    for domain in domains:
        response[domain] = get_domain_tags(
            domain=domain,
            es_client=es_client,
            content=params.content,
            min_score=params.min_score,
            constant_score=bool(params.constant_score),
            offset=params.offset,
            limit=params.limit,
        )
    return response
