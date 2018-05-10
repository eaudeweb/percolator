import logging
from elasticsearch_dsl import DocType, Text, Percolator, Search
from elasticsearch_dsl.query import Query


log = logging.getLogger(__name__)

INDEX = 'species_percolator'


class QueryDoc(DocType):
    """Document type for percolating queries storage"""
    query = Percolator()
    content = Text()

    class Meta:
        index = INDEX
        doc_type = '_doc'


class PercolateQuery(Query):
    """
    Required to 'register' the `percolate` query name.
    Percolating with `Search` will not work without it
    """
    name = 'percolate'


class SpeciesTagger:

    def __init__(self, client, species_path=None):
        self.client = client
        QueryDoc.init()  # Create the mappings

        if species_path:
            self.species = self.get_species(species_path)
            self.register_queries()

    @staticmethod
    def get_species(species_path):
        """
        Reads species from file at the provided path.
        Returns:
            A set of species names.
        """
        log.debug('Fetching species ...')
        species = []
        for line in open(species_path, 'r').readlines():
            sl = line.strip().lower()
            if sl:
                species.append(sl)
        return set(species)

    def register_queries(self):
        """Saves the species names as query documents"""

        def mk_query_body(term):
            return {'match': {'content': term}}

        log.debug('Registering queries')
        for s in self.species:
            q = QueryDoc(query=mk_query_body(s))
            q.save()

    def get_tags(self, content, min_score=None, offset=None, limit=None):
        """
        Percolates the provided content.

        Returns:
            A list of (matched content, score) tuples.
        """
        log.debug('Fetching tags ...')
        s = Search(using=self.client, index=INDEX).query(
            'percolate', field='query', document={'content': content}
        )

        if min_score is not None:
            s = s.extra(min_score=min_score)

        if offset is not None and limit is not None:
            s = s[offset:offset + limit]
        elif offset is not None:
            s = s[int(offset):]
        elif limit is not None:
            s = s[:limit]

        response = s.execute()
        return [(hit.query.match.content, hit.meta.score) for hit in response]
