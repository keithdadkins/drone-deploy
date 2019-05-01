#!/bin/bash
# Configures drone's docker-compose and Caddy file using configs stored in the
# aws parameter store. Permissions for accessing the parameter store are baked into the
# drone server instance profile, and the DRONE_DEPLOYMENT_ID should be set in /etc/environment

# aws command
aws="docker run --rm aws-cli aws"
region=

# We look for template files (the below files with '.template' appended to them) to parse, and
# the results are created with these names
compose_file="/home/ubuntu/docker-compose.yaml"
caddy_file="/home/ubuntu/Caddyfile"

# parameters (normal config parameters and secret config parameters)
configs=('DRONE_AWS_REGION' 'DRONE_SERVER_HOST' 'DRONE_SERVER_DOCKER_IMAGE' 'DRONE_AGENT_DOCKER_IMAGE')
secrets=('DRONE_ADMIN' 'DRONE_ADMIN_EMAIL' 'DRONE_USER_FILTER' 'DRONE_RPC_SECRET' 'DRONE_GITHUB_CLIENT_ID' 'DRONE_GITHUB_CLIENT_SECRET')

# wait for meta-data service (MS_WAIT_TIME is in seconds)
MS_WAIT_TIME=120
wait_for_metadata(){
    local up=

    # it may take a bit for the meta-data service to be available
    for i in {1..$MS_WAIT_TIME}; do
        if (curl http://169.254.169.254/latest/dynamic/instance-identity/document/ | grep region) > /dev/null 2>&1; then
            up=true
            break
        else
            sleep 1
        fi
    done

    if ! $up; then
        # meta-data did not return a document within the wait time
        exit 1
    fi
}


# get the current aws region from aws's meta-data service
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


# replace vals in compose template
update_files() {
    local search=$1
    local replace=$2

    sed -i "s|\\\${$search}|${replace}|g" "$compose_file.temp"
    sed -i "s|\\\${$search}|${replace}|g" "$caddy_file.temp"
}


main(){
    # set region and key prefix
    prefix="drone.$DRONE_DEPLOYMENT_ID"
    set_region > /dev/null 2>&1

    # fetch and update non-secret configs in the compose file
    for config in "${configs[@]}"; do
        param=$(get_parameter "$config")
        update_files "$config" "$param"
    done

    # fetch and update the secrets
    for secret in "${secrets[@]}"; do
        param=$(get_secret_parameter "$secret")
        update_files "$secret" "$param"
    done

    # backup the existing config if present
    if [ -f "$compose_file"]; then
        local dstamp=$(date +"%Y%m%d%H%M")
        cp "$compose_file" "$compose_file.$dstamp.bak" && cp "$compose_file.template" "$compose_file"
    fi
    mv "$compose_file.temp" "$compose_file"

    # backup caddy
    if [ -f "$caddy_file"]; then
        local dstamp=$(date +"%Y%m%d%H%M")
        cp "$caddy_file" "$caddy_file.$dstamp.bak" && cp "$caddy_file.template" "$caddy_file"
    fi
    mv "$caddy_file.temp" "$caddy_file"
}

# make a copy of the compose template. we will parse it, then replace the existing one (if present) 
# after doing a backup in the main() function.
cp "$compose_file.template" "$compose_file.temp"
cp "$caddy_file.template" "$caddy_file.temp"
wait_for_metadata && main
