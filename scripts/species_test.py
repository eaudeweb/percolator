#!/usr/bin/env python

import sys
import logging
from elasticsearch_dsl.connections import connections
from percolator.conf import settings
from percolator.search import BaseTagger, SpeciesQueryIndexer

log = logging.getLogger('percolator_search')
log.setLevel(logging.INFO)

client = connections.create_connection(hosts=settings.ELASTICSEARCH_HOSTS, timeout=20)
indexer = SpeciesQueryIndexer(client=client)
tagger = BaseTagger(indexer=indexer)
if len(sys.argv) > 1:
    with open(sys.argv[1], 'r') as f:
        tags = tagger.get_tags(text=f.read(), constant_score=False)
        for tag, score in tags.items():
            print(f'{tag.capitalize():50} {score:>.2f}')
