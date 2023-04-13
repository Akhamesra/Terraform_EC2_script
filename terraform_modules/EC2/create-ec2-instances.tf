terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
  backend "s3" {
    key            = "batch_keynotprovided/terraform.tfstate"
  }
}

provider "aws" {
    region  = var.aws_region
    profile = var.aws_profile
}

data "aws_subnets" "example" {
  filter {
    name   = "vpc-id"
    values = [var.vpc_id]
  }
}

data "aws_subnet" "all" {
  for_each = toset(data.aws_subnets.example.ids)
  id       = each.value
}

data "aws_instances" "existing_instances" {
  instance_tags = {
    Name = "BFL-PRCS-AIRFLOWCLS-WORKER*"
  }
}

locals {
  max_available = max(values(data.aws_subnet.all)[*].available_ip_address_count...) 
  # subnetid = [for k, s in data.aws_subnet.all : s.id if s.available_ip_address_count == local.max_available][0]
  subnetid = [for k, s in data.aws_subnet.all : s.id if s.available_ip_address_count >= var.instance_count][0]
  instance_number = length(data.aws_instances.existing_instances.ids)
}
data "aws_iam_roles" "all_roles" {

  name_regex     = "AWS-QuickSetup-StackSet*"
}

output "roles_list" {
  value = data.aws_iam_roles.all_roles.names
}

# resource "aws_instance" "ec2_instancess" {
#   count         = var.instance_count
#   ami           = var.ami
#   instance_type = var.instancetype
#   subnet_id     = local.subnetid
#   tags = {
#     Name = "BFL-PRCS-AIRFLOWCLS-WORKER ${local.instance_number + count.index}"
#   }
#   provisioner "local-exec" {
#     command = "echo BFL-PRCS-AIRFLOWCLS-WORKER ${local.instance_number + count.index}: ${self.private_ip} >> instance_ips.txt"
#   }
# }


