#!/usr/bin/env python

import sys
import logging
from elasticsearch_dsl.connections import connections
from percolator.conf import settings
from percolator.search.countries import CountryQueryIndexer

logging.basicConfig()
log = logging.getLogger('percolator_search')
log.setLevel(logging.INFO)

client = connections.create_connection(hosts=settings.ELASTICSEARCH_HOSTS, timeout=20)
indexer = CountryQueryIndexer(client=client)
if len(sys.argv) > 2:
    indexer.index_queries(countries_path=sys.argv[1], synonyms_path=sys.argv[2])
