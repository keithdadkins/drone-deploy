# vpc
variable "vpc_id" {
    description = "The vpc id where you want drone to be deployed."
}

# drone-server ami
variable "drone_server_ami" {
    description = "The drone-server AMI used to launch the drone server ec2 instance."
}

# drone-server instance-type (t2.micro, etc.)
variable "drone_server_instance_type" {
    description = "Instance type for the drone server. Defaults to t2.micro"
    default = "t2.micro"
}

# deployment uuid
variable "drone_deployment_id" {
    description = "drone_deployment_id artifact generated during the bootstrap process. Used for tagging resources."
}

# domain, dns
variable "drone_server_hosted_zone" {
    description = "The name of the hosted zone for the drone server domain. E.g., 'podchaser.com', not 'drone.podchaser.com')"
}

variable "drone_server_machine_name" {
    description = "The name of the drone server host. E.g., 'drone' as in 'drone.podchaser.com'"
    default = "drone"
}

variable "is_hosted_zone_private" {
    description = "Is the drone_server_hosted_zone private?"
    default = false
}

# security group rules
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

# ec2 instance key-pair
variable "drone_server_key_pair_name" {
    description = "Name of the Key Pair to use to connect to the ec2 instance. You must create and download the keys manually."
}
