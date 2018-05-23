# Percolator

A document tagging webservice

TODO: what this tool can do

## System architecture

TODO: main components (Python/Apistar, Elastic Search, Tika, Nginx)

## Setting up a local environment

Prerequisites: Docker, Docker compose

Checklist:

1. Clone this repository
2. Copy `docker/percolator.env.example` to `docker/percolator.env` and edit.
3. Edit docker-compose.override.yml
4. Review other environment settings like ES_JAVA_OPTS and forwarded ports (see docker-compose.yml)
5. Run `docker-compose up` and check for errors
6. Initialize the index (see below)

## Initialize the indices

    docker-compose exec app bash
    export PYTHONPATH=`pwd`
    ./scripts/mk_species_index.py data/speciesplus/species.txt
    ./scripts/mk_country_index.py data/countries/countries.txt data/countries/countries_synonyms.txt

## Test

TODO: Supported URL's and some examples

## Development mode

* Override /var/local/percolator with your local copy of the source code

