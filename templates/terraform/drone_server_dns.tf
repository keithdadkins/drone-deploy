
# data source used to find our hosted zone id
data "aws_route53_zone" "drone-server" {
    name         = "${var.drone_server_hosted_zone}."
    private_zone = "${var.is_hosted_zone_private}"
}

# elastic ip
resource "aws_eip" "drone-server" {
    vpc = true
}

# associate our eip with the drone server instance
resource "aws_eip_association" "drone-server" {
    instance_id   = "${aws_instance.drone-server.id}"
    allocation_id = "${aws_eip.drone-server.id}"
}

# drone server A record
resource "aws_route53_record" "drone-server" {
    zone_id = "${data.aws_route53_zone.drone-server.zone_id}"
    name    = "${var.drone_server_machine_name}.${data.aws_route53_zone.drone-server.name}"
    type    = "A"
    records = ["${aws_eip.drone-server.public_ip}"]
    ttl     = "300"
}
