#!/usr/bin/env python

import sys
import logging
from elasticsearch_dsl.connections import connections
from percolator.search.species import SpeciesQueryIndexer

logging.basicConfig()
log = logging.getLogger('percolator_search')
log.setLevel(logging.INFO)

client = connections.create_connection(hosts=['localhost'], timeout=20)
indexer = SpeciesQueryIndexer(client=client, index='species_percolator')
if len(sys.argv) > 1:
    indexer.index_queries(tags_path=sys.argv[1])
