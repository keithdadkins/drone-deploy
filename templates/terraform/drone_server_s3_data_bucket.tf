
resource "aws_s3_bucket" "drone-data" {
    bucket = "drone-data.${var.drone_server_machine_name}.${var.drone_server_hosted_zone}"
    acl    = "private"
    policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyPublicReadACL",
      "Effect": "Deny",
      "Principal": {
        "AWS": "*"
      },
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl"
      ],
      "Resource": "arn:aws:s3:::drone-data.${var.drone_server_machine_name}.${var.drone_server_hosted_zone}*",
      "Condition": {
        "StringEquals": {
          "s3:x-amz-acl": [
            "public-read",
            "public-read-write",
            "authenticated-read"
          ]
        }
      }
    },
    {
      "Sid": "DenyPublicReadGrant",
      "Effect": "Deny",
      "Principal": {
        "AWS": "*"
      },
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl"
      ],
      "Resource": "arn:aws:s3:::drone-data.${var.drone_server_machine_name}.${var.drone_server_hosted_zone}*",
      "Condition": {
        "StringLike": {
          "s3:x-amz-grant-read": [
            "*http://acs.amazonaws.com/groups/global/AllUsers*",
            "*http://acs.amazonaws.com/groups/global/AuthenticatedUsers*"
          ]
        }
      }
    },
    {
      "Sid": "DenyPublicListACL",
      "Effect": "Deny",
      "Principal": {
        "AWS": "*"
      },
      "Action": "s3:PutBucketAcl",
      "Resource": "arn:aws:s3:::drone-data.${var.drone_server_machine_name}.${var.drone_server_hosted_zone}",
      "Condition": {
        "StringEquals": {
          "s3:x-amz-acl": [
            "public-read",
            "public-read-write",
            "authenticated-read"
          ]
        }
      }
    },
    {
      "Sid": "DenyPublicListGrant",
      "Effect": "Deny",
      "Principal": {
        "AWS": "*"
      },
      "Action": "s3:PutBucketAcl",
      "Resource": "arn:aws:s3:::drone-data.${var.drone_server_machine_name}.${var.drone_server_hosted_zone}",
      "Condition": {
        "StringLike": {
          "s3:x-amz-grant-read": [
            "*http://acs.amazonaws.com/groups/global/AllUsers*",
            "*http://acs.amazonaws.com/groups/global/AuthenticatedUsers*"
          ]
        }
      }
    },
    {
      "Sid": "ForceSecureTransport",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": "arn:aws:s3:::drone-data.${var.drone_server_machine_name}.${var.drone_server_hosted_zone}*",
      "Condition": {
        "Bool": {
          "aws:SecureTransport": "false"
        }
      }
    }
  ]
}
POLICY
}
