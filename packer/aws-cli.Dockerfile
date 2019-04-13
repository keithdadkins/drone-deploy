ARG CLI_BASE_IMAGE=python:3.7
FROM $CLI_BASE_IMAGE
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y awscli && \
    rm -rf /var/cache/apt/*

ENTRYPOINT ["aws"]
