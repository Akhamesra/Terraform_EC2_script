from flask.cli import AppGroup
import click
import boto3
import config.settings as AppSetting
import json
def getResource(aws_profile):
    session = boto3.session.Session(profile_name = aws_profile)
    resource = session.resource('ec2')
    return resource

ec2 = AppGroup('ec2')

@ec2.command('choosesubnet')
@click.option('-i', '--instance_count', required=True)
@click.option('--aws_profile',  required=True, default='default', help='AWS session profile')
def choosesubnet(instance_count,aws_profile):
    try:
        instance_count = int(instance_count)
        subnet_list = {}
        subnet_free_ips = {}
        ec2_resource = getResource(aws_profile)
        filters = [{'Name':'subnet-id', 'Values': AppSetting.subnets}]
        subnets = ec2_resource.subnets.filter(Filters=filters)
        for subnet in list(subnets):
            subnet_free_ips[subnet.id] = subnet.available_ip_address_count
        subnet_free_ips = dict(sorted(subnet_free_ips.items(), key=lambda x:x[1],reverse=True))
        total_available_ips = sum(subnet_free_ips.values())
        if total_available_ips<int(instance_count):
            print("Not Enough available ips")
            return False
        for k in subnet_free_ips:
            if instance_count>0:
                if instance_count>subnet_free_ips[k]:
                    subnet_list[k] = subnet_free_ips[k]
                    instance_count = instance_count - subnet_free_ips[k]
                else:
                    subnet_list[k] = instance_count
                    instance_count = 0
        # print(type(json.dumps(subnet_list)))
        return subnet_list
        # print(subnet_free_ips)
        # print(total_available_ips)
    except Exception as e:
        print(e)
