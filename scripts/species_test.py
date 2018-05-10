#!/usr/bin/env python

import sys
import logging
from elasticsearch_dsl.connections import connections
from percolator.search import SpeciesTagger

log = logging.getLogger('percolator_search')
log.setLevel(logging.INFO)

client = connections.create_connection(hosts=['localhost'], timeout=20)
tagger = SpeciesTagger(client=client)
if len(sys.argv) > 1:
    with open(sys.argv[1], 'r') as f:
        tags = tagger.get_tags(f.read())
        for tag in tags:
            print(f'{tag[0]:50} ({tag[1]:>.2f})')