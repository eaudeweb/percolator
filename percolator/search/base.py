import logging
from elasticsearch_dsl import DocType, Search, Index
from elasticsearch_dsl.query import Query

log = logging.getLogger('percolator_search')


class PercolateQuery(Query):
    """
    Required to 'register' the `percolate` query name.
    Percolating with `Search` will not work without it.
    """
    name = 'percolate'


class BaseQueryIndexer:

    query_doc_type = DocType
    query_type = 'match'
    field_name = 'content'

    def __init__(self, client):
        self.client = client
        self.query_doc_type.init()  # Create the mappings

    @property
    def index(self):
        return self.query_doc_type._doc_type.index

    @staticmethod
    def _read_tags(tags_path):
        """
        Reads tags from file at the provided path.
        Returns:
            A set of tag names.
        """
        log.info(f'Fetching tags from {tags_path}')
        tags = set()
        for line in open(tags_path, 'r').readlines():
            t = line.strip().lower()
            if t:
                tags.add(t)

        log.info(f'Read {len(tags)} unique tags')
        return tags

    def _mk_query_body(self, term):
        """Prepares a query body dict that matches `term`."""
        return {self.query_type: {self.field_name: term}}

    def index_queries(self, tags_path):
        """Saves the tag names as query documents"""
        log.info('Registering queries')
        tags = self._read_tags(tags_path)
        for t in tags:
            query_doc = self.query_doc_type(query=self._mk_query_body(t))
            query_doc.save()


class BaseTagger:
    """
    Base percolating search provider.

    Args:
        indexer: A `BaseQueryIndexer`-based instance.
    """

    def __init__(self, indexer):
        self.indexer = indexer

    @property
    def client(self):
        return self.indexer.client

    @property
    def index(self):
        return self.indexer.index

    @property
    def field_name(self):
        return self.indexer.field_name

    @property
    def query_type(self):
        return self.indexer.query_type

    def _search_query(self, content):
        return Search(using=self.client, index=self.index).query(
            'percolate', field='query', document={self.field_name: content}
        )

    def get_tags(self, content, min_score=None, offset=None, limit=None):
        """
        Percolates the provided content, with score filtering and paging.

        Args:
            content: The text to search for tags.
            min_score (float): The minimum search score required. No default is applied when not provided.
            offset (int): The paging offset - if missing ElasticSearch's `from` defaults to 0.
            limit (int): The paging limit - if missing ElasticSearch's `size` defaults to 10.
            Note that `size` acts as `offset + limit`.

        Returns:
            A list of (matched content, score) tuples.
        """
        log.info('Fetching tags ...')
        s = self._search_query(content)

        if min_score is not None:
            s = s.extra(min_score=min_score)

        if offset is not None and limit is not None:
            offset, limit = int(offset), int(limit)
            s = s[offset:offset + limit]
        elif offset is not None:
            offset = int(offset)
            s = s[int(offset):]
        elif limit is not None:
            limit = int(limit)
            s = s[:limit]

        response = s.execute()
        # Only return the matches and scores in hits
        return [
            (
                getattr(getattr(hit.query, self.query_type), self.field_name),
                hit.meta.score
            )
            for hit in response
        ]
