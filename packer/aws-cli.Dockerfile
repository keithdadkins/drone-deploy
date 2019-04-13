FROM python:3.7
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y awscli && \
    rm -rf /var/cache/apt/*

ENTRYPOINT ["aws"]
