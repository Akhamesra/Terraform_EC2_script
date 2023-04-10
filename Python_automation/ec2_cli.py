from flask.cli import AppGroup
import click
import boto3
import config.settings as AppSetting
import json
from botocore.exceptions import ClientError
import os

ec2_resource = boto3.resource('ec2')
ec2 = AppGroup('ec2')

@ec2.command('choosesubnet')
@click.option('-i', '--instance_count', required=True)
def choosesubnet(instance_count):
    filters = [{'Name':'subnet-id', 'Values': AppSetting.subnets}]
    subnets = ec2_resource.subnets.filter(Filters=filters)
    for subnet in list(subnets):
        free_ips = subnet.available_ip_address_count
        # n = int(subnet.cidr_block.split('/')[1])
        # cidr_ips = 2**(32-n)
        # used_ips = cidr_ips - free_ips
        # print('{:s}: cidr={:d}, aws used=5, you used={:d}, free={:d}'.\
        #     format(subnet.id, cidr_ips, used_ips - 5, free_ips))
        if int(instance_count)<= free_ips:
            print(subnet.id)
            return subnet.id
        else:
            return False