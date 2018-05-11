import logging
from elasticsearch_dsl import (Index, DocType, Text, Percolator, token_filter, analyzer)

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

    @staticmethod
    def abbr_species(species):
        """
        Abbreviates the first word in species name, e.g.:
            'capricornis thar' -> 'c. thar'
        """
        parts = species.split(' ')
        if len(parts) < 2:
            return None

        return f'{parts[0][0]} {" ".join(parts[1:])}'

    @staticmethod
    def autophrase_species(species):
        """
        Contracts multi-word species for autophrasing, i.e.:
            'capricornis thar' -> 'capricornis_thar'
        """
        return '_'.join(species.split(' '))

    def synonyms(self, species):
        """
        Builds the synonym lists.

        Two synonyms steps are performed and result in lists:
         - species (and abbreviations if available) are autophrased
         - autophrased species and abbreviations are synonymized.

        Returns:
            tuple of string lists
        """
        syns = []
        autophrase_syns = []
        for s in species:
            autophrase = self.autophrase_species(s)
            autophrase_syns.append(f'{s} => {autophrase}')
            abbr = self.abbr_species(s)
            if abbr is not None:
                autophrase_abbr = self.autophrase_species(abbr)
                autophrase_syns.append(f'{abbr} => {autophrase_abbr}')
                syns.append(f'{autophrase}, {autophrase_abbr}')

        return autophrase_syns, syns

    def index_queries(self, tags_path):
        """
        (Re)Creates the index with synonyms, and saves the species names as query documents.
        """
        log.info('Registering queries')
        species = self.get_tags(tags_path)

        index = Index(self.index)
        index.doc_type(self.query_doc_type)

        autophrase_syns, syns = self.synonyms(species)

        autophrase_filter = token_filter(
            f'species_autophrase_syn', type='synonym', synonyms=autophrase_syns
        )

        syn_filter = token_filter(
            f'species_syn', type='synonym', tokenizer='keyword', synonyms=syns
        )

        species_analyzer = analyzer(
            f'species_analyzer',
            tokenizer='standard',
            filter=[autophrase_filter, syn_filter],
        )
        index.analyzer(species_analyzer)
        index.delete(ignore=404)
        index.create()

        for s in species:
            query_doc = self.query_doc_type(query=self.mk_query_body(s))
            query_doc.save()
