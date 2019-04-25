# get the current aws user identity
data "aws_caller_identity" "current" { }

# set aws region
provider "aws" {
  region              = "${var.aws_region}"
}

# drone-server instance
resource "aws_instance" "drone-server" {
    ami             = "${var.drone_server_ami}"
    instance_type   = "${var.drone_server_instance_type}"
    iam_instance_profile = "${aws_iam_instance_profile.drone-builder.name}"
    vpc_security_group_ids = ["${aws_security_group.drone-server.id}"]
    key_name = "${var.drone_server_key_pair_name}"
    
    tags {
        Name = "drone-server"
        drone_deployment_id = "${var.drone_deployment_id}"
    }
}

# associate our eip with the drone server instance
resource "aws_eip_association" "drone-server" {
    instance_id   = "${aws_instance.drone-server.id}"
    allocation_id = "${aws_eip.drone-server.id}"
}

# # output messages
# output "drone-server-ssh" {
#     value = <<-CONFIG

#         add to your ~/.ssh/config for quick ssh access (replace with path to your key pair)
#         once added, connect with 'ssh "${aws_route53_record.drone-server.fqdn}"'
#         ---
#         # ~/.ssh/config
#         Host "${aws_route53_record.drone-server.fqdn}"
# 	        HostName "${aws_route53_record.drone-server.fqdn}"
# 	        User ubuntu
# 	        IdentityFile ~/.ssh/PATH_TO_YOUR_KEY_PAIR.pem
#     CONFIG
# }
