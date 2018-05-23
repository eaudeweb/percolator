import logging
from elasticsearch_dsl import (Index, DocType, Text, Percolator, token_filter, analyzer)

from .base import BaseQueryIndexer, BaseTagger

log = logging.getLogger('percolator_search')


class CountryQueryDoc(DocType):
    """Document type for percolating queries storage"""
    query = Percolator()
    content = Text(analyzer='country_analyzer')

    class Meta:
        doc_type = '_doc'


class CountryQueryIndexer(BaseQueryIndexer):

    index = 'country_percolator'
    query_doc_type = CountryQueryDoc
    query_type = 'match_phrase'
    field_name = 'content'

    @staticmethod
    def _analyzer(synonyms):

        syn_filter = token_filter(
            f'country_syn', type='synonym', tokenizer='keyword', synonyms=synonyms
        )

        return analyzer(
            f'country_analyzer',
            tokenizer='lowercase',
            filter=[
                syn_filter
            ],
        )

    def index_queries(self, countries_path, synonyms_path):
        """
        (Re)Creates the index with synonyms, and saves the country query documents.
        """
        countries = self._read_tags(countries_path)
        synonyms = self._read_tags(synonyms_path)

        index = Index(self.index)
        index.doc_type(self.query_doc_type)

        log.info('Building analyzer')
        index.analyzer(self._analyzer(synonyms))

        log.info('(Re)Creating index')
        index.delete(ignore=404)
        index.create()

        log.info('Registering queries')
        for c in countries:
            query_doc = self.query_doc_type(query=self._mk_query_body(c))
            query_doc.save()


class CountryTagger(BaseTagger):
    def get_tags(self, *args, **kwargs):
        tags = super().get_tags(*args, **kwargs)
        tags = {' '.join(w.capitalize() or ' ' for w in k.split()): v for k, v in tags.items()}
        return tags
