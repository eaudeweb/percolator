FROM python:3.6-slim

ARG REQUIREMENTS_FILE=requirements.txt

ENV PYTHONUNBUFFERED=1
ENV APP_HOME=/var/local/percolator

#RUN runDeps="..." \
# && apt-get update -y \
# && apt-get install -y --no-install-recommends $runDeps \
# && apt-get clean \
# && rm -vrf /var/lib/apt/lists/*

RUN mkdir -p $APP_HOME

COPY requirements.txt $APP_HOME
WORKDIR $APP_HOME

RUN pip install --no-cache-dir -r $REQUIREMENTS_FILE

COPY . $APP_HOME

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["run"]
