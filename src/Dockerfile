FROM r.compredict.xyz/library/python:3.10-slim

ENV VIRTUAL_ENV=/app/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app
COPY requirements.txt /app/
COPY requirements_lock.txt /app/

RUN pip install -r requirements_lock.txt \
    && pip install etna[prophet]

COPY run_all.py /app/
COPY run_all_config.yaml /app/
COPY models /app/models
COPY data /app/data
COPY docker-entrypoint.sh /app/

RUN mkdir -p /data/interim /data/predicted

ENTRYPOINT ["/app/docker-entrypoint.sh"]
