from flask.cli import AppGroup
import click
import boto3
import config.settings as AppSetting

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
        ec2_resource = getResource(aws_profile)
        filters = [{'Name':'subnet-id', 'Values': AppSetting.subnets}]
        subnets = ec2_resource.subnets.filter(Filters=filters)
        for subnet in list(subnets):
            free_ips = subnet.available_ip_address_count
            n = int(subnet.cidr_block.split('/')[1])
            cidr_ips = 2**(32-n)
            used_ips = cidr_ips - free_ips
            print('{:s}: cidr={:d}, aws used=5, you used={:d}, free={:d}'.\
                format(subnet.id, cidr_ips, used_ips - 5, free_ips))
            # if int(instance_count)<= free_ips:
            #     print(subnet.id)
            #     return subnet.id
            # else:
            #     return False
    except Exception as e:
        print(e)