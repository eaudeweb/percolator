from apistar import Route
from .views import *


routes = [
    Route('/domains', method='GET', handler=list_tag_domains),
    Route('/tag', method='POST', handler=extract_from_json),
    Route('/tag/form', method='POST', handler=extract_from_form),
    Route('/tag/url', method='POST', handler=extract_from_url),
]
