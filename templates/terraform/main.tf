# get the current aws user identity
data "aws_caller_identity" "current" { }

# set aws region
provider "aws" {
  region              = "${var.drone_aws_region}"
}

# drone-server instance
resource "aws_instance" "drone-server" {
    ami             = "${var.drone_server_ami}"
    instance_type   = "${var.drone_server_instance_type}"
    iam_instance_profile = "${aws_iam_instance_profile.drone-builder.name}"
    vpc_security_group_ids = ["${aws_security_group.drone-server.id}"]
    key_name = "${var.drone_server_key_pair_name}"
    
    tags = {
        Name = "${var.drone_deployment_name}-DroneCI"
        Owner = "${data.aws_caller_identity.current.user_id}"
        deployment_id = "${var.drone_deployment_id}"
    }
}
