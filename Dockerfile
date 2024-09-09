FROM python:3.12-alpine3.20
ARG ENVIRONMENT
ENV PYTHONUNBUFFERED 1
RUN mkdir /source
WORKDIR /source
ADD . /source/
RUN apk update && apk add --no-cache bash gcc musl-dev python3-dev libpq-dev
RUN pip3 install -r requirements/base.txt &&\
    if [ "$ENVIRONMENT" = "local" ]; then \
    pip3 install -r requirements/local.txt; \
    fi
COPY . /source/
