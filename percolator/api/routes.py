from apistar import Route
from .views import *


routes = [
    Route('/extract/species', method='POST', handler=extract_species),
]
