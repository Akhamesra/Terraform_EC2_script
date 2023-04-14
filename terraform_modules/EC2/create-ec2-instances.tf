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

# data "aws_instances" "existing_instances" {
#   filter {
#     name   = "tag:Name"
#     values = ["BFL-PRCS-AIRFLOWCLS-WORKER*"]
#   }
#   # tags = {
#   #   Name = "BFL-PRCS-AIRFLOWCLS-WORKER*"
#   # }
# }

# output "instance_name" {
#   value = [for id in data.aws_instances.existing_instances.ids : id]
# }


locals {
  max_available = max(values(data.aws_subnet.all)[*].available_ip_address_count...) 
  # subnetid = [for k, s in data.aws_subnet.all : s.id if s.available_ip_address_count == local.max_available][0]
  subnetid = [for k, s in data.aws_subnet.all : s.id if s.available_ip_address_count >= var.instance_count][0]
  instance_number = 50
}
resource "aws_network_interface" "eni1" {
    subnet_id        = var.subnetid
}
resource "aws_instance" "ec2_instancess" {
  count         = var.instance_count
  ami           = var.ami
  instance_type = var.instancetype
  subnet_id     = var.subnetid
  tags = {
    Name = "BFL-PRCS-AIRFLOWCLS-WORKER ${local.instance_number + count.index}"
    CREATION_DATE = formatdate("YYYY-MM-DD", timestamp())
  }
  provisioner "local-exec" {
    command = "echo BFL-PRCS-AIRFLOWCLS-WORKER ${local.instance_number + count.index}: ${self.private_ip} >> instance_ips.txt"
  }
}


