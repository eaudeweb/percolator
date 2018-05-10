from apistar import App

from .routes import routes
from .components import ElasticSearchClientComponent
from percolator.conf import settings

components = [
    ElasticSearchClientComponent(hosts=settings.ELASTICSEARCH_HOSTS)
]

app = App(routes=routes, components=components)
