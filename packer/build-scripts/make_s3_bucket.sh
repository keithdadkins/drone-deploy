#!/usr/bin/env bash
DRONE_DEPLOYMENT_ID=${DRONE_DEPLOYMENT_ID:-}
DRONE_REGION=${DRONE_REGION:-}

bucket_name="drone-data-$DRONE_DEPLOYMENT_ID"
set -euo pipefail

printf "\n\n\n\n***** CONFIGURING S3 STORAGE *****\n\n\n\n"

# fail if env vars are not set
var_fail_message="must be set to create the drone storage bucket... exiting."
[ -z "$DRONE_DEPLOYMENT_ID" ] && echo "DRONE_DEPLOYMENT_ID $var_fail_message" && exit 1
[ -z "$DRONE_REGION" ] && echo "DRONE_REGION $var_fail_message" && exit 1


# set our $aws command (just a shortcut instead of writing out a long docker run ... command everytime)
get_docker_cmd(){
    local docker_cmd='docker'
    [ "$EUID" -eq 0 ] && docker_cmd="sudo docker"
    echo "$docker_cmd"
}
aws="$(get_docker_cmd) run --rm aws-cli -- aws"

# create the s3 bucket
echo "Configuring drone storage:"
printf "    creating s3 bucket... "
if $aws s3 mb "s3://$bucket_name" --region="$DRONE_REGION" > /dev/null 2>&1; then
    echo "OK"
else
    printf "\nError creating bucket... exiting." && exit 1
fi

# load our bucket policy from disk and use bash's pattern replacement to replace all occurrences of '$bucket_name'
# with the value of $bucket_name var ${data//pattern_to_search_for/string_to_replace_with}. e.g., poor mans templating
bucket_policy="$(<s3_bucket_policy.json)"
bucket_policy="${bucket_policy//\$bucket_name/$bucket_name}"

# attach the policy to the bucket
printf "    applying security policy... "
if $aws s3api put-bucket-policy --bucket "$bucket_name" --policy "$bucket_policy" > /dev/null 2>&1; then
    echo "OK"
else
    printf "\nError attaching ./s3_bucket_policy.json to the bucket... exiting." && exit 1
fi

# Block all public acccess and the ability to add public objects
bucket_public_access_block=$(cat <<'EOF'
{
    "PublicAccessBlockConfiguration": {
        "BlockPublicAcls": true,
        "IgnorePublicAcls": true,
        "BlockPublicPolicy": true,
        "RestrictPublicBuckets": true
    }
}
EOF
)

printf "    blocking public access... "
if $aws s3api put-public-access-block --bucket "$bucket_name" --cli-input-json "$bucket_public_access_block" > /dev/null 2>&1; then
    echo "OK"
else
    printf "\nError putting public access blocks in place... exiting." && exit 1
fi

# encrypt the bucket
encryption_policy=$(cat <<'EOF'
{
    "ServerSideEncryptionConfiguration": {
        "Rules": [
            {
                "ApplyServerSideEncryptionByDefault": {
                    "SSEAlgorithm": "AES256"
                }
            }
        ]
    }
}
EOF
)

printf "    setting default encryption... "
if $aws s3api put-bucket-encryption --bucket "$bucket_name" --cli-input-json "$encryption_policy" > /dev/null 2>&1; then
    echo "OK"
else
    printf "\nError enabling default encryption... exiting." && exit 1
fi

# tag with drone-deployment-id
bucket_tags="$(cat <<EOF
{
  "TagSet": [
    {
      "Key": "drone_deployment_id",
      "Value": "$DRONE_DEPLOYMENT_ID"
    }
  ]
}
EOF
)"

printf "    tagging bucket... "
if $aws s3api put-bucket-tagging --bucket "$bucket_name" --tagging "$bucket_tags" > /dev/null 2>&1; then
    echo "OK"
else
    printf "\nError tagging s3 bucket... exiting." && exit 1
fi

echo ""
echo "Drone storage bucket successfully configured:"
echo "  name: $bucket_name"
echo "  sse: AES256"
