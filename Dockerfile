FROM python:3.8-slim-buster

RUN pip3 install -U pipenv

RUN mkdir -p /var/app
WORKDIR /var/app
COPY . /var/app
RUN pipenv sync
RUN bin/tests
