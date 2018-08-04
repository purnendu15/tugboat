ARG FROM=python:3.6
FROM ${FROM}

VOLUME /var/tugboat
WORKDIR /var/tugboat

ARG ctx_base=.

COPY ${ctx_base}/requirements.txt /opt/tugboat/requirements.txt
RUN pip3 install --no-cache-dir -r /opt/tugboat/requirements.txt

COPY ${ctx_base} /opt/tugboat
RUN pip3 install -e /opt/tugboat
