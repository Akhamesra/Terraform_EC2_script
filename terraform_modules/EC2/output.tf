output "public_ips" {
  value = aws_instance.ec2_instancess.*.public_ip
} 