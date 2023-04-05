terraform {
  backend "s3" {
    # Replace this with your bucket name!
    key            = var.instace_count
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
  ami           = "ami-0e742cca61fb65051" 
  instance_type = "t2.micro"
  tags = {
    Name = "VS Instance ${local.instance_number + count.index}"
  }
}


