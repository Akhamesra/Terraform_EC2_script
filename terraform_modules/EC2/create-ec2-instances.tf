terraform {
  backend "s3" {
    key            = "batch_keynotprovided/terraform.tfstate"
  }
}

data "aws_instances" "existing_instances" {
  instance_tags = {
    Name = "VS Instance*"
  }
}

locals {
  instance_number = length(data.aws_instances.existing_instances.ids)
}

resource "aws_instance" "ec2_instancess" {
  count = var.instance_count
  ami           = var.ami
  instance_type = var.instancetype
  subnet_id = var.subnetid
  tags = {
    Name = "VS Instance ${local.instance_number + count.index}"
  }
}


