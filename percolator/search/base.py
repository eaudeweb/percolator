import logging
from elasticsearch_dsl import DocType, Search
from elasticsearch_dsl.query import Query

log = logging.getLogger('percolator_search')


class PercolateQuery(Query):
    """
    Required to 'register' the `percolate` query name.
    Percolating with `Search` will not work without it.
    """
    name = 'percolate'


class BaseTagger:
    """
    Base percolating search provider.

    Args:
        client: A `Elasticsearch` client.

    Attributes:
        query_doc_type: A `DocType`-based query document implementation.
        field_name: The name of content field on the query document.
    """

    query_doc_type = DocType
    field_name = ''

    def __init__(self, client):
        self.client = client

    def get_search_query(self, content):
        return Search(using=self.client, index=self.query_doc_type._doc_type.index).query(
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
        s = self.get_search_query(content)

        if min_score is not None:
            s = s.extra(min_score=min_score)

        if offset is not None and limit is not None:
            s = s[offset:offset + limit]
        elif offset is not None:
            s = s[int(offset):]
        elif limit is not None:
            s = s[:limit]

        response = s.execute()
        return [
            (getattr(hit.query.match, self.field_name), hit.meta.score)
            for hit in response
        ]


class BaseQueryIndexer:

    query_doc_type = DocType
    field_name = 'content'

    def __init__(self, client):
        self.client = client
        self.query_doc_type.init()  # Create the mappings

    @staticmethod
    def get_tags(tags_path):
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

    def mk_query_body(self, term):
        """Prepares a query body dict that matches `term`."""
        return {'match': {self.field_name: term}}

    def register_queries(self, tags_path):
        """Saves the tag names as query documents"""
        log.info('Registering queries')
        tags = self.get_tags(tags_path)
        for t in tags:
            query_doc = self.query_doc_type(query=self.mk_query_body(t))
            query_doc.save()
