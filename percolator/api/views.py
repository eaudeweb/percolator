from apistar import App, validators
from apistar.http import Response, QueryParam
from apistar.exceptions import BadRequest
from elasticsearch import Elasticsearch

from ..search import TAG_DOMAINS
from .components import MultiPartForm
from ..core.types import CoercingType
from ..core.text import extract_text, extract_text_from_url
from ..core.exceptions import TextExtractionError, TextExtractionTimeout


def list_tag_domains(es_client: Elasticsearch) -> dict:
    """
    Lists tag domains.

    Returns:
        dict mapping domain names to their descriptions.
    """
    domains = TAG_DOMAINS.values()
    return {
        d.name: {
            'description': d.description,
            'tags_count': d.query_indexer(client=es_client).count()
        }
        for d in domains
    }


class DomainValidator(validators.String):
    """Custom string validator for domains"""
    errors = {'exact': 'Unknown domain', 'enum': f'Unknown domain'}


class BaseExtractionJSONParams(CoercingType):
    """Common extraction parameters validator"""
    domains = validators.Array(
        items=DomainValidator(enum=list(TAG_DOMAINS.keys())),
        unique_items=True,
        description='List of domains to search, if not provided ALL domains will be included',
        allow_null=True,
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


class TextExtractionJSONParams(BaseExtractionJSONParams):
    """Validator for raw text content extraction parameters."""
    text = validators.String(
        max_length=1024 * 1024 * 10,
        default='',
        allow_null=True,
        description='Text to be analyzed for species mentions',
    )


class URLExtractionJSONParams(BaseExtractionJSONParams):
    """Validator for URL content extraction parameters."""
    url = validators.String(
        max_length=400,
        allow_null=True,
        description='URL of document to fetch and analyze',
    )


def get_domain_tags(
    domain,
    es_client,
    text,
    min_score=None,
    constant_score=True,
    offset=None,
    limit=None,
):
    """Fetches tags for a domain"""
    tag_domain = TAG_DOMAINS[domain]
    indexer = tag_domain.query_indexer(client=es_client)
    tagger = tag_domain.tagger(indexer=indexer)
    return tagger.get_tags(
        text=text,
        min_score=min_score,
        constant_score=constant_score,
        offset=offset,
        limit=limit,
    )


def extract_from_text(params: TextExtractionJSONParams, es_client: Elasticsearch) -> dict:
    """Tag extraction endpoint handler, accepts parameters as JSON."""
    if not params.text:
        raise BadRequest({'content': 'Required and not provided'})

    domains = params.domains or TAG_DOMAINS.keys()
    response = {}
    for domain in domains:
        response[domain] = get_domain_tags(
            domain=domain,
            es_client=es_client,
            text=params.text,
            min_score=params.min_score,
            constant_score=bool(params.constant_score),
            offset=params.offset,
            limit=params.limit,
        )
    return response


def extract_from_url(params: URLExtractionJSONParams, es_client: Elasticsearch) -> dict:
    try:
        text = extract_text_from_url(params.url)
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
            text=text,
            min_score=params.min_score,
            constant_score=bool(params.constant_score),
            offset=params.offset,
            limit=params.limit,
        )
    return response


def extract_from_form(form_data: MultiPartForm, es_client: Elasticsearch) -> dict:
    """
    Tag extraction endpoint handler, accepting a multi-part form.
    """
    params = dict(form_data)  # Convert from ImmutableDict
    params = {k: v[0] for k, v in params.items()}  # Strip array wrappers from fields

    domains = params.get('domains')
    if domains:
        params['domains'] = [d.strip() for d in domains.split(',')]
    else:
        params['domains'] = []

    try:
        source = params.pop('source')
    except KeyError:
        raise BadRequest({'source': 'Required and not provided'})

    try:
        params['constant_score'] = params.pop('constant_score') == 'on'
    except KeyError:
        params['constant_score'] = True

    print(params)

    if source == 'text':
        try:
            params = TextExtractionJSONParams.validate(params, allow_coerce=True)
        except validators.ValidationError as exc:
            print('bad text params')
            raise BadRequest(exc.detail)
        return extract_from_text(params, es_client)
    elif source == 'url':
        try:
            params = URLExtractionJSONParams.validate(params, allow_coerce=True)
        except validators.ValidationError as exc:
            raise BadRequest(exc.detail)
        return extract_from_url(params, es_client)

    try:
        file = params.pop('file')
    except KeyError:
        raise BadRequest({'file': 'Required and not provided'})

    try:
        params = BaseExtractionJSONParams.validate(params, allow_coerce=True)
    except validators.ValidationError as exc:
        raise BadRequest(exc.detail)

    try:
        text = extract_text(file.stream)
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
            text=text,
            min_score=params.min_score,
            constant_score=bool(params.constant_score),
            offset=params.offset,
            limit=params.limit,
        )
    return response


def home(app: App):
    return app.render_template('home.html')
