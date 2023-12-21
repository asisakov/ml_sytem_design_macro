FROM r.compredict.xyz/library/python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

ENTRYPOINT ["/app/docker-entrypoint.sh"]
