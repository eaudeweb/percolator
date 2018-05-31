#!/usr/bin/env python

import sys
import logging
from elasticsearch_dsl.connections import connections
from percolator.conf import settings
from percolator.search.species import SpeciesTaxonIndexer

logging.basicConfig()
log = logging.getLogger('percolator_search')
log.setLevel(logging.INFO)

client = connections.create_connection(hosts=settings.ELASTICSEARCH_HOSTS, timeout=20)
indexer = SpeciesTaxonIndexer(client=client)
if len(sys.argv) > 1:
    indexer.index_taxa(taxa_path=sys.argv[1])