variable "instance_count" {
  description = "Number of EC2 instances to create"
  type        = number
  default =  2
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
