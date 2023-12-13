FROM r.compredict.xyz/library/python:3.10-slim

WORKDIR /app
COPY . /app

ENV VIRTUAL_ENV=/app/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install -r requirements_lock.txt

ENTRYPOINT ["/app/docker-entrypoint.sh"]
