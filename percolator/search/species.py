import logging
from elasticsearch_dsl import DocType, Text, Percolator

from .base import BaseTagger, BaseQueryIndexer


log = logging.getLogger('percolator_search')


INDEX = 'species_percolator'


class SpeciesQueryDoc(DocType):
    """Document type for percolating queries storage"""
    query = Percolator()
    content = Text()

    class Meta:
        index = INDEX
        doc_type = '_doc'


class SpeciesTagger(BaseTagger):

    query_doc_type = SpeciesQueryDoc
    field_name = 'content'


class SpeciesQueryIndexer(BaseQueryIndexer):

    query_doc_type = SpeciesQueryDoc
    field_name = 'content'
