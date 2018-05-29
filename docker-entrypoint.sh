#!/bin/sh

mkdir static_files
cp -r static/* static_files

# Copy apistar package static files
mkdir static_files/apistar
cp -r /usr/local/lib/python3.6/site-packages/apistar/static/* static_files/apistar

case "$1" in
    build_index)
        exec python scripts/mk_species_index.py data/samples/species.txt
        ;;
    run)
        exec gunicorn percolator.api:app \
            --bind 0.0.0.0:5000 \
            --access-logfile=- \
            --worker-class=meinheld.gmeinheld.MeinheldWorker
        ;;
    *)
esac
