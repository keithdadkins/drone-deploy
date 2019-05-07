# TODO create a separate set of roles and policies for the drone-server instance
# For now, just share with the drone-builder role (it's safe to do so)

# drone-builder role with policy that defines who can assume this role
resource "aws_iam_role" "drone-builder" {
    name               = "${var.drone_deployment_name}-builder"
    path               = "/"
    assume_role_policy = <<-POLICY
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "ec2.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            },
            {
                "Effect": "Allow",
                "Principal": {
                    "AWS": "${data.aws_caller_identity.current.arn}"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    POLICY
       
    tags = {
        Name = "${var.drone_deployment_name}-DroneCI"
        Owner = "${data.aws_caller_identity.current.user_id}"
        deployment_id = "${var.drone_deployment_id}"
    }
}

# ec2 policy that contains the minimum set of perms for packer to build the ami,
# get secrets from the paramter store, and to pass roles to the ec2 instance
resource "aws_iam_policy" "drone-builder-ec2" {
    name        = "${var.drone_deployment_name}-ec2"
    path        = "/"
    description = ""
    policy      = <<-POLICY
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Resource": "*",
                "Action": [
                    "ec2:AttachVolume",
                    "ec2:AuthorizeSecurityGroupIngress",
                    "ec2:CopyImage",
                    "ec2:CreateImage",
                    "ec2:CreateKeypair",
                    "ec2:CreateSecurityGroup",
                    "ec2:CreateSnapshot",
                    "ec2:CreateTags",
                    "ec2:CreateVolume",
                    "ec2:DeleteKeypair",
                    "ec2:DeleteSecurityGroup",
                    "ec2:DeleteSnapshot",
                    "ec2:DeleteVolume",
                    "ec2:DeregisterImage",
                    "ec2:DescribeImageAttribute",
                    "ec2:DescribeImages",
                    "ec2:DescribeInstances",
                    "ec2:DescribeRegions",
                    "ec2:DescribeSecurityGroups",
                    "ec2:DescribeSnapshots",
                    "ec2:DescribeSubnets",
                    "ec2:DescribeTags",
                    "ec2:DescribeVolumes",
                    "ec2:DetachVolume",
                    "ec2:GetPasswordData",
                    "ec2:ModifyImageAttribute",
                    "ec2:ModifyInstanceAttribute",
                    "ec2:ModifySnapshotAttribute",
                    "ec2:RegisterImage",
                    "ec2:RunInstances",
                    "ec2:StopInstances",
                    "ec2:TerminateInstances",
                    "ec2:RequestSpotInstances",
                    "ec2:CancelSpotInstanceRequests",
                    "ec2:AssociateIamInstanceProfile",
                    "ec2:ReplaceIamInstanceProfileAssociation",
                    "ec2:RequestSpotInstances",
                    "ec2:CancelSpotInstanceRequests",
                    "ec2:DescribeSpotInstanceRequests",
                    "iam:PassRole"
                ]
            },
            {
                "Effect": "Allow",
                "Action": "sts:AssumeRole",
                "Resource": [
                    "${aws_iam_role.drone-builder.arn}"
                ]
            },
            {
                "Effect":"Allow",
                "Action":[
                    "ssm:DescribeParameters",
                    "ssm:GetParameter",
                    "ssm:GetParametersByPath"
                ],
                "Resource":[
                    "arn:aws:ssm:${var.drone_aws_region}:${data.aws_caller_identity.current.account_id}:parameter/drone/${var.drone_deployment_id}/*"
                ]
            }
        ]
    }
    POLICY
}

# this policy enables the builder to create and manage a deployments s3 bucket, and blocks
# everyone else (notice the "StringLike" and "StringNotLike" in the conditions
resource "aws_iam_policy" "drone-builder-s3" {
    name        = "${var.drone_deployment_name}-s3"
    path        = "/"
    description = "GrantBuilderRoleDenyEveryoneElse"
    policy      = <<-POLICY
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AllowBuilderToManageBucket",
                "Effect": "Allow",
                "Action": [
                    "s3:*"
                ],
                "Resource": [
                    "arn:aws:s3:::${var.drone_s3_bucket}/*"
                ],
                "Condition": {
                    "StringLike": {
                        "aws:userid": [
                            "${aws_iam_role.drone-builder.unique_id}:*",
                            "${data.aws_caller_identity.current.account_id}"
                        ]
                    }
                }
            },
            {
                "Sid": "DenyEveryoneButBuilder",
                "Effect": "Deny",
                "Action": "s3:*",
                "Resource": [
                    "arn:aws:s3:::${var.drone_s3_bucket}/*"
                ],
                "Condition": {
                    "StringNotLike": {
                        "aws:userId": [
                            "${aws_iam_role.drone-builder.unique_id}:*",
                            "${data.aws_caller_identity.current.account_id}"
                        ]
                    }
                }
            }
        ]
    }
    POLICY
}

# attach the ec2 and s3 policies to the drone-builder-role
resource "aws_iam_policy_attachment" "ec2" {
    name       = "${var.drone_deployment_name}-ec2-attach"
    policy_arn = "${aws_iam_policy.drone-builder-ec2.arn}"
    groups     = []
    users      = []
    roles      = ["${var.drone_deployment_name}-builder"]
}

resource "aws_iam_policy_attachment" "s3" {
    name       = "${var.drone_deployment_name}-s3-attach"
    policy_arn = "${aws_iam_policy.drone-builder-s3.arn}"
    groups     = []
    users      = []
    roles      = ["${var.drone_deployment_name}-builder"]
}

# instance profile used to pass roles to our EC2 instance when it starts.
# https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_switch-role-ec2_instance-profiles.html
resource "aws_iam_instance_profile" "drone-builder" {
  name  = "${var.drone_deployment_name}-builder"
  role = "${aws_iam_role.drone-builder.name}"
}

output "DRONE_BUILDER_ROLE_ARN" {
  value = "${aws_iam_role.drone-builder.arn}"
}
