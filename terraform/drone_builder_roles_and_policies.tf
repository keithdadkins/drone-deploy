# Attach the ec2 and s3 policies to the drone-builder role and allow the ec2
# instance to assume that role. This allows the ec2 instance to interact 
# with ec2 and s3 without needing to supply aws credentials (e.g., AWS_ACCESS_KEY's)

# drone-builder role (with assume role permissions)
resource "aws_iam_role" "drone-builder" {
    name               = "drone-builder-role"
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
}

# this is the ec2 policy for the drone-builder role. The minimum perms for packer to do its thing.
# it also allows the ec2 instance to assume the ec2 and s3 p
resource "aws_iam_policy" "drone-builder-ec2" {
    name        = "drone-builder-ec2-policy"
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
            }
        ]
    }
    POLICY
}

# this policy restricts access to 'drone-data-*' buckets to anyone but 
# the ec2 instance's assumed drone-builder-role.
resource "aws_iam_policy" "drone-builder-s3" {
    name        = "drone-builder-s3-policy"
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
                    "arn:aws:s3:::drone-data-*"
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
                    "arn:aws:s3:::drone-data-*"
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

# attache ec2 and s3 policies to the drone-builder-role
resource "aws_iam_policy_attachment" "ec2" {
    name       = "drone-builder-ec2-policy-attachment"
    policy_arn = "${aws_iam_policy.drone-builder-ec2.arn}"
    groups     = []
    users      = []
    roles      = ["drone-builder-role"]
}

resource "aws_iam_policy_attachment" "s3" {
    name       = "drone-builder-s3-policy-attachment"
    policy_arn = "${aws_iam_policy.drone-builder-s3.arn}"
    groups     = []
    users      = []
    roles      = ["drone-builder-role"]
}

# the profile to launch our ec2 instance with
resource "aws_iam_instance_profile" "drone-builder" {
  name  = "drone-builder"
  role = "${aws_iam_role.drone-builder.name}"
}
