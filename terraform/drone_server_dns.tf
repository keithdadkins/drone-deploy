
# data source used to find our hosted zone id
data "aws_route53_zone" "drone-server" {
    name         = "${var.drone_server_hosted_zone}."
    private_zone = "${var.is_hosted_zone_private}"
}

# elastic ip
resource "aws_eip" "drone-server" {
    vpc = true
}

# drone server A record
resource "aws_route53_record" "drone-server" {
    zone_id = "${data.aws_route53_zone.drone-server.zone_id}"
    name    = "${var.drone_server_machine_name}.${data.aws_route53_zone.drone-server.name}"
    type    = "A"
    records = ["${aws_eip.drone-server.public_ip}"]
    ttl     = "300"
}
