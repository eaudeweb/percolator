import logging
from elasticsearch_dsl import (Index, DocType, Text, Percolator, token_filter, analyzer)

from .base import BaseQueryIndexer, BaseTagger

log = logging.getLogger('percolator_search')


class SpeciesQueryDoc(DocType):
    """Document type for percolating queries storage"""
    query = Percolator()
    content = Text(analyzer='species_analyzer')

    class Meta:
        doc_type = '_doc'


class SpeciesQueryIndexer(BaseQueryIndexer):

    index = 'species_percolator'
    query_doc_type = SpeciesQueryDoc
    query_type = 'match_phrase'
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

    def _synonyms(self, species):
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

    def _analyzer(self, species, dump=True):
        autophrase_syns, syns = self._synonyms(species)

        if dump:
            with open('autophrase_syns.txt', 'w') as f:
                f.writelines(l + '\n' for l in autophrase_syns)

            with open('syns.txt', 'w') as f:
                f.writelines(l + '\n' for l in syns)

        autophrase_filter = token_filter(
            f'species_autophrase_syn', type='synonym', synonyms=autophrase_syns
        )

        syn_filter = token_filter(
            f'species_syn', type='synonym', tokenizer='keyword', synonyms=syns
        )

        return analyzer(
            f'species_analyzer',
            tokenizer='lowercase',
            filter=[
                autophrase_filter,
                syn_filter
            ],
        )

    def index_queries(self, tags_path):
        """
        (Re)Creates the index with synonyms, and saves the species names as query documents.
        """
        species = self._read_tags(tags_path)

        index = Index(self.index)
        index.doc_type(self.query_doc_type)

        log.info('Building analyzer')
        index.analyzer(self._analyzer(species))

        log.info('(Re)Creating index')
        index.delete(ignore=404)
        index.create()

        log.info('Registering queries')
        for s in species:
            query_doc = self.query_doc_type(query=self._mk_query_body(s))
            query_doc.save()


class SpeciesTagger(BaseTagger):
    def get_tags(self, *args, **kwargs):
        tags = super().get_tags(*args, **kwargs)
        tags = {k.capitalize(): v for k, v in tags.items()}
        return tags