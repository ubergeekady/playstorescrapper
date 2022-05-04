FROM python:3.6-alpine

RUN adduser -D playstoreapi

WORKDIR /home/playstoreapi

RUN apk update && apk add libressl-dev postgresql-dev libffi-dev gcc musl-dev python3-dev libxml2 libxslt libxml2-dev libxslt-dev
COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install --upgrade pip
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY . .
RUN chmod +x boot.sh

RUN chown -R playstoreapi:playstoreapi ./
USER playstoreapi

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]