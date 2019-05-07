variable "drone_deployment_name" {
    description = "A unique name for the drone deployment."
}

variable "drone_deployment_id" {
    description = "drone_deployment_id artifact generated during the bootstrap process. Used for tagging resources."
}

variable "drone_vpc_id" {
    description = "The vpc_id to deploy in."
}

variable "drone_aws_region" {
    description = "The aws region to deploy in."
}

variable "drone_server_host" {
    description = "The full URL that agents will use to connect to the server. ex https://drone.yourdomain.com"
}

variable "drone_server_docker_image" {
    description = "The server docker image. Get this from https://hub.docker.com/r/drone/drone/tags"
    default = "drone/drone:latest"
}

variable "drone_agent_docker_image" {
    description = "The agent docker image. Get this from https://hub.docker.com/r/drone/agent/tags"
    default = "drone/agent:latest"
}

variable "drone_github_server" {
    description = "The full URL to the GitHub Server."
    default = "https://github.com"
}

variable "drone_admin" {
    description = "The GitHub username of the deployments administrator."
}

variable "drone_admin_email" {
    description = "Email address for the admin. This is needed for auto TLS registration with Let's Encrypt"
}

variable "drone_user_filter" {
    description = "List of GitHub usernames to allow access to Drone CI"
}

variable "drone_rpc_secret" {
    description = "A shared secret used to authenticate communication between agents and the server."
}

variable "drone_github_client_id" {
    description = "OAuth client id. Create and get from https://github.com/settings/developers."
}

variable "drone_github_client_secret" {
    description = "OAuth client secret. Create and get from https://github.com/settings/developers."
}

variable "drone_server_ami" {
    description = "The drone-server AMI used to launch the drone server ec2 instance."
}

variable "drone_server_instance_type" {
    description = "Instance type for the drone server. Defaults to t2.micro"
    default = "t2.micro"
}

variable "drone_server_hosted_zone" {
    description = "The name of the hosted zone for the drone server domain. E.g., 'yourdomain.com', not 'drone.yourdomain.com')"
}

variable "drone_server_machine_name" {
    description = "The name of the drone server host. E.g., 'drone' as in 'drone.yourdomain.com'"
}

variable "is_hosted_zone_private" {
    description = "Is the drone_server_hosted_zone private?"
    default = false
}

variable "drone_server_allow_ssh" {
    type = "list"
    description = "Array of ip addresses allowed to access ssh/port 22."
}

variable "drone_server_allow_http" {
    type = "list"
    description = "Array of ip addresses allowed to access the drone server via http/port 80. Must be open for auto tls certs."
    default = ["0.0.0.0/0"]
}

variable "drone_server_allow_https" {
    type = "list"
    description = "Array of ip addresses allowed to access the drone server via https/port 443. Must be open for auto tls certs."
    default = ["0.0.0.0/0"]
}

variable "drone_server_key_pair_name" {
    description = "Name of the Key Pair to use to connect to the ec2 instance. You must create and download the keys manually."
}

variable "drone_s3_bucket" {
    description = "Name of the s3 bucket to store build logs and drone backups."
}
