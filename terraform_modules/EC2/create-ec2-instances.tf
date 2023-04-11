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

data "aws_subnet" "info" {
  vpc_id = "vpc-047278c6bb3919d49"
}

data "aws_subnet" "all" { 
  for_each = data.aws_subnet.info.ids
  id = each.value
}

data "aws_instances" "existing_instances" {
  instance_tags = {
    Name = "BFL-PRCS-AIRFLOWCLS-WORKER*"
  }
}

locals {
  max_available = max(values(data.aws_subnet.all)[*].available_ip_address_count...)
  subnetid = [for k, s in data.aws_subnet.all : s.id if s.available_ip_address_count == local.max_available][0]
  instance_number = length(data.aws_instances.existing_instances.ids)
}

resource "aws_instance" "ec2_instancess" {
  count         = var.instance_count
  ami           = var.ami
  instance_type = var.instancetype
  subnet_id     = local.subnetid
  tags = {
    Name = "BFL-PRCS-AIRFLOWCLS-WORKER ${local.instance_number + count.index}"
  }
  provisioner "local-exec" {
    command = "echo BFL-PRCS-AIRFLOWCLS-WORKER ${local.instance_number + count.index}: ${self.public_ip} >> instance_ips.txt"
  }
}


