resource "aws_security_group" "drone-server" {
    name        = "${var.drone_deployment_name}-server"
    description = "${var.drone_deployment_name}-server-sg-access-rules"
    vpc_id      = "${var.drone_vpc_id}"

    ingress {
        from_port       = 80
        to_port         = 80
        protocol        = "tcp"
        cidr_blocks     = ["${var.drone_server_allow_http}"]
    }

    ingress {
        from_port       = 443
        to_port         = 443
        protocol        = "tcp"
        cidr_blocks     = ["${var.drone_server_allow_https}"]
    }

    ingress {
        from_port       = 22
        to_port         = 22
        protocol        = "tcp"
        cidr_blocks     = ["${var.drone_server_allow_ssh}"]
    }

    egress {
        from_port       = 0
        to_port         = 0
        protocol        = "-1"
        cidr_blocks     = ["0.0.0.0/0"]
    }

    tags = {
        Name = "${var.drone_deployment_name}-DroneCI"
        Owner = "${data.aws_caller_identity.current.user_id}"
        deployment_id = "${var.drone_deployment_id}"
    }

}
