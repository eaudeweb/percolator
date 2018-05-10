import logging
from apistar.server.components import Component
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
