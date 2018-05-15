from apistar import Route
from .views import *


routes = [
    Route('/extract/species/txt', method='POST', handler=extract_species),
    Route('/extract/species/bin', method='POST', handler=extract_species_from_file),
]
