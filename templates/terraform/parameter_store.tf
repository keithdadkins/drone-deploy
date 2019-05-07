# map of parameter configs
locals {
    params = {
        DRONE_AWS_REGION = "${var.drone_aws_region}",
        DRONE_SERVER_HOST = "${var.drone_server_host}",
        DRONE_SERVER_DOCKER_IMAGE = "${var.drone_server_docker_image}",
        DRONE_AGENT_DOCKER_IMAGE = "${var.drone_agent_docker_image}",
        DRONE_GITHUB_SERVER = "${var.drone_github_server}",
        DRONE_S3_BUCKET = "${var.drone_s3_bucket}"
    },
    secret_params = {
        DRONE_ADMIN = "${var.drone_admin}",
        DRONE_ADMIN_EMAIL = "${var.drone_admin_email}",
        DRONE_USER_FILTER = "${var.drone_user_filter}",
        DRONE_RPC_SECRET = "${var.drone_rpc_secret}",
        DRONE_GITHUB_CLIENT_ID = "${var.drone_github_client_id}",
        DRONE_GITHUB_CLIENT_SECRET = "${var.drone_github_client_secret}"
    }
}

# for each parameter
resource "aws_ssm_parameter" "paramaters" {
    count = "${length(keys(local.params))}"
    type = "String"
    name = "/drone/${var.drone_deployment_id}/${element(keys(local.params), count.index)}"
    value = "${element(values(local.params), count.index)}"
    tags = {
        Name = "${var.drone_deployment_name}-DroneCI"
        Owner = "${data.aws_caller_identity.current.user_id}"
        deployment_id = "${var.drone_deployment_id}"
    }
}

# for each secret (uses default kms)
resource "aws_ssm_parameter" "secret-paramaters" {
    count = "${length(keys(local.secret_params))}"
    type = "SecureString"
    name = "/drone/${var.drone_deployment_id}/${element(keys(local.secret_params), count.index)}"
    value = "${element(values(local.secret_params), count.index)}"
    tags = {
        Name = "${var.drone_deployment_name}-DroneCI"
        Owner = "${data.aws_caller_identity.current.user_id}"
        deployment_id = "${var.drone_deployment_id}"
    }
}
