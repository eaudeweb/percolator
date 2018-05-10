import sys
from elasticsearch_dsl.connections import connections
from percolator.search import SpeciesTagger


if __name__ == '__main__':
    client = connections.create_connection(hosts=['localhost'], timeout=20)
    tagger = SpeciesTagger(client=client)
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            tags = tagger.get_tags(f.read())
            for tag in tags:
                print(f'{tag[0]:50} ({tag[1]:>.2f})')