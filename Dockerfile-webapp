FROM ubuntu:20.04

ADD . /app
WORKDIR /app

RUN apt-get update && \
    apt-get install python3 python3-venv python3-dev libgeoip-dev build-essential -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
RUN python3.8 -m venv venv && \
    venv/bin/pip3.8 install wheel && \
    venv/bin/pip3.8 install -r requirements.txt

CMD venv/bin/python3.8 index.py
