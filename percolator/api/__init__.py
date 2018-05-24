from apistar import App

from .routes import routes
from .components import (
    ElasticSearchClientComponent, RequestStreamComponent, MultiPartParserComponent
)
from percolator.conf import settings

components = [
    ElasticSearchClientComponent(hosts=settings.ELASTICSEARCH_HOSTS),
    RequestStreamComponent(),
    MultiPartParserComponent(),
]

app = App(
    routes=routes,
    components=components,
    static_dir=settings.STATIC_DIR,
    template_dir=settings.TEMPLATES_DIR,
)
