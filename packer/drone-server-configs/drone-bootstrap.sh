#!/bin/bash
# Configures drone's docker-compose file using configs stored in the
# aws parameter store. Permissions for accessing the parameter store are baked into the
# drone server instance profile, and the DRONE_DEPLOYMENT_ID should be set in /etc/environment

# aws command
aws="docker run --rm aws-cli aws"
region=

# get the servers region
set_region(){
    local meta="$(curl http://169.254.169.254/latest/dynamic/instance-identity/document/)"
    region=$(docker run --rm aws-cli /bin/sh -c "echo '$meta' | jq .region | xargs")
}

# gets a parameter from the parameter store
get_parameter(){
    local param=
    local val=
    if param=$($aws ssm get-parameter --region $region --name "drone.$DRONE_DEPLOYMENT_ID.$1"); then
	val="$(docker run --rm aws-cli /bin/sh -c "echo '$param' | jq .Parameter.Value | xargs")"
        echo "$val"
    else
        return 1
    fi
}

# gets a secret parameter from the parameter store
get_secret_parameter(){
    local param=
    local val=
    if param=$($aws ssm get-parameter --with-decryption --region $region --name "drone.$DRONE_DEPLOYMENT_ID.$1"); then
	val="$(docker run --rm aws-cli /bin/sh -c "echo '$param' | jq .Parameter.Value | xargs")"
        echo "$val"
    else
        return 1
    fi
}

# replace config variable with param in /home/ubuntu/docker-compose.yaml
update_compose_file() {
    local search=$1
    local replace=$2

    sed -i "s/\\\${$search}/${replace}/g" /home/ubuntu/docker-compose.yaml
}

# set region and key prefix
prefix="drone.$DRONE_DEPLOYMENT_ID"
set_region > /dev/null 2>&1

# fetch and update non-secret configs in the compose file
configs=('DRONE_REGION' 'DRONE_SERVER_HOST' 'DRONE_IMAGE')
for config in "${configs[@]}"; do
    param=$(get_parameter "$config")
    update_compose_file "$config" "$param"
done

# fetch and update the secrets
secrets=('DRONE_ADMIN' 'DRONE_USER_FILTER' 'DRONE_RPC_SECRET' 'DRONE_GITHUB_CLIENT_ID' 'DRONE_GITHUB_CLIENT_SECRET')
for secret in "${secrets[@]}"; do
    param=$(get_secret_parameter "$secret")
    update_compose_file "$secret" "$param"
done
