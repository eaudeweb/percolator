#!/bin/sh

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
