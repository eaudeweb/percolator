import logging
import io
import typing
from apistar import http
from apistar.server.wsgi import WSGIEnviron
from apistar.server.components import Component
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug.formparser import FormDataParser
from werkzeug.http import parse_options_header
from werkzeug.wsgi import get_input_stream

from elasticsearch import Elasticsearch
from elasticsearch_dsl.connections import connections

log = logging.getLogger(__name__)


class ElasticSearchClientComponent(Component):
    def __init__(self, hosts):
        self.client = connections.create_connection(hosts=hosts, timeout=20)
        log.info('ElasticSearch connection created')
        log.debug(f'ElasticSearch connection to {hosts}')

    def resolve(self) -> Elasticsearch:
        return self.client


RequestStream = typing.NewType('RequestStream', io.BufferedIOBase)
MultiPartForm = typing.NewType('MultiPartForm', ImmutableMultiDict)


class RequestStreamComponent(Component):
    def resolve(self, environ: WSGIEnviron) -> RequestStream:
        return get_input_stream(environ)


class MultiPartParserComponent(Component):

    @staticmethod
    def _get_content_length(headers: http.Headers) -> typing.Optional[int]:
        content_length = headers.get('Content-Length')
        if content_length is not None:
            try:
                return max(0, int(content_length))
            except (ValueError, TypeError):
                pass
        return None

    @staticmethod
    def _get_mimetype_and_options(headers: http.Headers) -> typing.Tuple[str, dict]:
        return parse_options_header(headers.get('Content-Type'))

    def resolve(self, headers: http.Headers, stream: RequestStream) -> MultiPartForm:
        mimetype, options = self._get_mimetype_and_options(headers)
        content_length = self._get_content_length(headers)
        parser = FormDataParser()
        stream, form, files = parser.parse(stream, mimetype, content_length, options)
        return ImmutableMultiDict(list(form.items()) + list(files.items()))
