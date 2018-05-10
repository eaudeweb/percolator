from apistar import Route
from .views import *


routes = [
    Route('/tag', method='POST', handler=tag),
]
