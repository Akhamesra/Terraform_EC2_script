variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-south-1"
}

variable "aws_profile" {
  description = "AWS profile"
  type        = string
  default     = "default"
}

variable "instance_count" {
  description = "Number of EC2 instances to create"
  type        = number
  default =  1
}

variable "ami" {
  description = "AMI ID of EC2 instance to create"
  type        = string
  default =  "ami-0e742cca61fb65051"
}

variable "instancetype" {
  description = "Instance type of EC2 instance to create"
  type        = string
  default =  "t2.micro"
}

variable "subnetid"{
  type = string
  default = ""
}


