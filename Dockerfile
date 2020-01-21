FROM python:3.8-slim-buster

WORKDIR /var/app
COPY . /var/app
RUN pip install --no-cache -e .