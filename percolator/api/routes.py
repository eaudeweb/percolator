from apistar import Route
from .views import *


routes = [
    Route('/tag/domains', method='GET', handler=list_tag_domains),
    Route('/tag/extract/species/txt', method='POST', handler=extract_species),
    Route('/tag/extract/species/bin', method='POST', handler=extract_species_from_file),
]
