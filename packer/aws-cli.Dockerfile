ARG CLI_BASE_IMAGE=python:3.7
FROM $CLI_BASE_IMAGE
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y \
        awscli \
        jq \
        openssl \
        && \
        rm -rf /var/cache/apt/*

COPY aws-cli-entrypoint-script.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh && \
    ln -s usr/local/bin/entrypoint.sh /

ENTRYPOINT ["/entrypoint.sh"]
