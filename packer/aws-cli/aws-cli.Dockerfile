ARG CLI_BASE_IMAGE=python:3.7-stretch
FROM $CLI_BASE_IMAGE
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y \
        jq \
        openssl \
        less \
        groff \
        && \
        rm -rf /var/cache/apt/*

# install python stuff (awscli, boto3, pyyaml, etc)
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt

COPY aws-cli-entrypoint-script.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh && \
    ln -s usr/local/bin/entrypoint.sh /

ENTRYPOINT ["/entrypoint.sh"]
