from apistar import Route
from .views import *


routes = [
    Route('/', method='GET', handler=home),
    Route('/domains', method='GET', handler=list_tag_domains),
    Route('/tag', method='POST', handler=extract_from_text),
    Route('/tag/url', method='POST', handler=extract_from_url),
    Route('/tag/form', method='POST', handler=extract_from_form),
]
