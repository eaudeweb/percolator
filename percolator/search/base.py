import logging
import csv
from elasticsearch_dsl import DocType, Search, Index, Q
from elasticsearch_dsl.query import Query
from elasticsearch.helpers import bulk

log = logging.getLogger('percolator_search')


class PercolateQuery(Query):
    """
    Required to 'register' the `percolate` query name.
    Percolating with `Search` will not work without it.
    """
    name = 'percolate'


class BaseQueryIndexer:

    index = None
    query_doc_type = DocType
    query_type = 'match'
    field_name = 'content'

    def __init__(self, client):
        self.client = client

    @staticmethod
    def _read_tags(tags_path, lowercase=True):
        """
        Reads tags from file at the provided path.
        Returns:
            A list of tag names.
        """
        log.info(f'Fetching tags from {tags_path}')
        tags = set()
        for line in open(tags_path, 'r').readlines():
            t = line.strip()
            if lowercase:
                t = t.lower()
            if t:
                tags.add(t)

        log.info(f'Read {len(tags)} unique tags')
        return list(tags)

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

    def count(self):
        return Search(using=self.client, index=self.index).count()


class BaseTagger:
    """
    Base percolating search provider.

    Args:
        indexer: A `BaseQueryIndexer`-based instance.
    """

    max_results = 10000  # Don't exceed 10k, this is the ES max window size

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

    def _search_query(self, text, constant_score=True):
        if constant_score:
            return Search(using=self.client, index=self.index).query(
                'constant_score',
                filter=Q('percolate', field='query', document={self.field_name: text}),
            )

        return Search(using=self.client, index=self.index).query(
            'percolate', field='query', document={self.field_name: text}
        )

    def _percolate(
        self, text, min_score=None, constant_score=True, offset=None, limit=None
    ):
        """
        Percolates the provided text, with score filtering and paging.

        Args:
            text: The text to percolate.
            min_score (float): The minimum search score required. No default is applied when not provided.
                Ignored when `constant_score` is on.
            constant_score (bool): Apply a `constant_score` wrapper on the search query.
                All results will have score `1`. This is on by default.
            offset (int): The paging offset - if missing ElasticSearch's `from` defaults to 0.
            limit (int): The paging limit - if missing ElasticSearch's `size` defaults to 10.
            Note that `size` acts as `offset + limit`.

        Returns: the search response object.
        """

        limit = int(limit or self.max_results)

        log.info('Fetching tags ...')
        s = self._search_query(text, constant_score)

        if min_score is not None and not constant_score:
            s = s.extra(min_score=min_score)

        if offset is not None:
            offset = int(offset)
            s = s[offset:offset + limit]
        else:
            s = s[:limit]

        return s.execute()

    def get_tags(
        self, text, min_score=None, constant_score=True, offset=None, limit=None
    ):
        """
        Percolates the provided text, with score filtering and paging.

        Args: see `_percolate()`

        Returns:
            A dict of tags and their scores. Note that the score is always `1` if `constant_score` is on.
        """

        response = self._percolate(text, min_score, constant_score, offset, limit)

        # Only return the matches and scores in hits
        return {
            getattr(
                getattr(hit.query, self.query_type), self.field_name
            ): hit.meta.score
            for hit in response
        }


class BaseTaxonIndexer:

    index = None
    doc_type = DocType
    query_type = 'match'
    field_names = []
    normalize_field_names = []
    autophrase_field_names = []

    def __init__(self, client):
        self.client = client

    @staticmethod
    def _normalize(term):
        return term.lower().replace('"', '')

    def _autophrase(self, term, normalize_first=True):
        if normalize_first:
            term = self._normalize(term)
        return '_'.join(term.split())

    def _read_taxa(self, taxa_path, delimiter=';'):
        """
        Generator of taxa processed from the CSV file at the provided path.
        """
        log.info(f'Fetching taxa from {taxa_path}')
        with open(taxa_path, 'r') as csv_file:
            reader = csv.DictReader(
                csv_file, fieldnames=self.field_names, delimiter=delimiter
            )
            for row in reader:
                taxon = {}
                for field_name, value in row.items():
                    if field_name in self.autophrase_field_names:
                        value = self._autophrase(value)
                    elif field_name in self.normalize_field_names:
                        value = self._normalize(value)
                    taxon[field_name] = value
                yield taxon

    def index_taxa(self, taxa_path):
        """Bulk-indexes the taxa"""
        index = Index(self.index)
        index.doc_type(self.doc_type)

        log.info('(Re)Creating index')
        index.delete(ignore=404)
        index.create()

        actions = (
            {'_index': self.index, '_type': self.doc_type._doc_type.name, '_source': t}
            for t in self._read_taxa(taxa_path)
        )

        log.info('Indexing taxa')
        bulk(self.client, actions)
        log.info(f'Indexed {self.count()} taxa')

    def count(self):
        return Search(using=self.client, index=self.index).count()

    def _search_query(self, **terms):
        search_terms = {}
        for field_name, value in terms.items():
            if field_name in self.autophrase_field_names:
                value = self._autophrase(value)
            elif field_name in self.normalize_field_names:
                value = self._normalize(value)
            search_terms[field_name] = value
        return Search(using=self.client, index=self.index).query(
            self.query_type, **search_terms
        )

    def search(self, **terms):
        query = self._search_query(**terms)
        results = query.execute()
        return [hit.to_dict() for hit in results]

    def first(self, **terms):
        matches = self.search(**terms)
        if not matches:
            return None

        return matches[0]
