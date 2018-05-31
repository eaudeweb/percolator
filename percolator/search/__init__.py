import attr
from .base import BaseTagger, BaseQueryIndexer, BaseTaxonIndexer
from .species import SpeciesQueryIndexer, SpeciesTagger, SpeciesTaxonIndexer
from .countries import CountryTagger, CountryQueryIndexer


def _validate_ancestor(attribute, value, ancestor_cls):
    if value != ancestor_cls and ancestor_cls not in getattr(value, '__bases__', []):
        raise ValueError(f'"{attribute.name}" must be descendant of {ancestor_cls.__name__}')


def is_query_indexer(instance, attribute, value):
    _validate_ancestor(attribute, value, BaseQueryIndexer)


def is_taxon_indexer(instance, attribute, value):
    _validate_ancestor(attribute, value, BaseTaxonIndexer)


def is_tagger(instance, attribute, value):
    _validate_ancestor(attribute, value, BaseTagger)


@attr.s
class Domain:
    name = attr.ib(validator=attr.validators.instance_of(str))
    query_indexer = attr.ib(validator=is_query_indexer)
    taxon_indexer = attr.ib(validator=attr.validators.optional(validator=is_taxon_indexer))
    tagger = attr.ib(validator=is_tagger)
    description = attr.ib(validator=attr.validators.instance_of(str))


_domains = [
    Domain(
        name='speciesplus',
        query_indexer=SpeciesQueryIndexer,
        taxon_indexer=SpeciesTaxonIndexer,
        tagger=SpeciesTagger,
        description='Species listed in the Appendices of CITES and CMS, as well as other CMS Family '
                    'listings and species included in the Annexes to the EU Wildlife Trade Regulations.'
    ),
    Domain(
        name='countries',
        query_indexer=CountryQueryIndexer,
        taxon_indexer=None,
        tagger=CountryTagger,
        description='Countries'
    ),
]

TAG_DOMAINS = {d.name: d for d in _domains}
