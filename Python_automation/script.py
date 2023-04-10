from flask.cli import AppGroup
import click
import boto3
import config.settings as AppSetting
import json
from botocore.exceptions import ClientError

ec2_resource = boto3.resource('ec2')
# Use this for specific subnets
ec2 = AppGroup('ec2')

@ec2.command('choosesubnet')
@click.option('-i', '--instance_count', required=True)
def choosesubnet(instance_count):
    filters = [{'Name':'subnet-id', 'Values':['subnet-051895ae60c4f447d','subnet-0390f0184f9c6c81a','subnet-082071928fe3e5a8f']}]
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
    

s3_resource = boto3.resource('s3')

s3 = AppGroup('s3')

@s3.command('downloadFile')
def downloadFile():
    bucketname = AppSetting.bucketname
    # objectpath = AppSetting.batchNumber['path']
    # objectname = AppSetting.batchNumber['name']
    objectname_number = AppSetting.objectnumber['paths3']+AppSetting.objectnumber['name'] #S3/path/number
    objectpath_number = AppSetting.objectnumber['pathlocal'] +AppSetting.objectnumber['name'] #local/path/number
    try:
        s3_resource.Object(bucketname,objectname_number).download_file(objectpath_number)
        print('File Downloaded')
    except ClientError as ce:
        if (ce.response['Error']['Message']=="Not Found"):
            with open(objectpath_number,'w+') as f:
                f.write('1')
            print("File Created")
        else:
            print(ce)
    except Exception as error:
        print(error)

def increamentbatch(objectpath):
    with open(objectpath, "r") as f:
        number = int(f.read())
    number += 1
    with open(objectpath, "w") as f:
        f.write(str(number))

def getUrl(key):
    bucketname = "akshitkhamesraautomation"
    url = boto3.client('s3').generate_presigned_url(
                                        ClientMethod='get_object',
                                        Params={
                                            'Bucket': bucketname,
                                            'Key': key
                                        }
                                    )
    print(url)
@s3.command('uploadFile')
def uploadFile():
    try:
        bucketname = AppSetting.bucketname #S3 name

        objectname_number = AppSetting.objectnumber['paths3']+AppSetting.objectnumber['name'] #S3/path/number
        objectpath_number = AppSetting.objectnumber['pathlocal'] +AppSetting.objectnumber['name'] #local/path/number
        increamentbatch(objectpath_number)

        objectname_ip = AppSetting.objectip['paths3']+AppSetting.objectip['name'] #S3/path/instances_ips.txt
        objectpath_ip = AppSetting.objectip['pathlocal'] +AppSetting.objectip['name'] #local/path/instances_ips.txt

        # objectname = file #S3/path
        
        # objectpath = AppSetting.objectapth+objectname #local/path
        # objectname_number = number  
        # if file=='number':
        #     increamentbatch(objectpath)
        s3_resource.Object(bucketname,objectname_number).upload_file(objectpath_number, ExtraArgs={'ACL':'public-read'})
        s3_resource.Object(bucketname,objectname_ip).upload_file(objectpath_ip, ExtraArgs={'ACL':'public-read'})
        print('Files Upload')
        getUrl(objectname_ip)
    except Exception as ce:
        print(ce)

@s3.command('deleteFile')
def deleteFile():
        try:
            bucketname = AppSetting.bucketname
            objectname_number = AppSetting.objectnumber['paths3']+AppSetting.objectnumber['name'] #S3/path/number
            objectname_ip = AppSetting.objectip['paths3']+AppSetting.objectip['name'] #S3/path/instances_ips.txt
            s3_resource.Object(bucketname, objectname_number).delete()
            print('number file deleted')
            s3_resource.Object(bucketname, objectname_ip).delete()
            print(bucketname)
            print(objectname_ip)
            print('instance_ips file deleted')
        except ClientError as ce:
            print(f"{ce.response['Error']['Code']} : {ce.response['Error']['Message']}")

ses = AppGroup('ses')

@ses.command('sendLaunchMail')
@click.option('--number_of_ec2')
def sendLaunchMail(number_of_ec2):  
        RECIPIENTS=AppSetting.recipients     
        # if(email.find('$$')!=-1):
        #     RECIPIENT=email.split('$$')  
        SENDER = AppSetting.sender['name'] + " <" + AppSetting.sender['email'] + ">"
        AWS_REGION = "ap-south-1"
        SUBJECT = "Instances Created"
        BODY_TEXT = "FROM TEAM DEVOPS"
        BODY_HTML = number_of_ec2+" EC2 instances created."
        CHARSET = "UTF-8"
        # client = self.getClient('ses', AWS_REGION)
        client = boto3.client('ses', region_name=AWS_REGION)
        try:
            response = client.send_email(
                Destination={
                    'ToAddresses': RECIPIENTS,
                },
                Message={
                    'Body': {
                        'Html': {
                            'Charset': CHARSET,
                            'Data': BODY_HTML,
                        },
                        'Text': {
                            'Charset': CHARSET,
                            'Data': BODY_TEXT,
                        },
                    },
                    'Subject': {
                        'Charset': CHARSET,
                        'Data': SUBJECT,
                    },
                },
                Source=SENDER,
            )
        except Exception as e:
            print('email sent fail : '+str(e))
            return False
        else:
            print('email sent')


def instanceCount():
    count=0
    try:
        with open('terraform_modules/EC2/file1.json') as f:
            data = json.load(f)
            for d in data['resource_changes']:
                if d['type']=='aws_instance':
                    count+=1
        return count
    except Exception as e:
        print(" !!! \n   No resource to delete, This batch has no instances running!\n !!!")
        return 0

@ses.command('sendTerminateMail')
def sendTerminateMail():
        instances = instanceCount()  
        RECIPIENT=AppSetting.recipients   
        # if(email.find('$$')!=-1):
        #     RECIPIENT=email.split('$$')  
        SENDER = AppSetting.sender['name'] + " <" + AppSetting.sender['email'] + ">"
        AWS_REGION = "ap-south-1"
        SUBJECT = "Instances Terminated"
        BODY_TEXT = "FROM TEAM DEVOPS"
        BODY_HTML = str(instances) +" EC2 instances terminated."
        CHARSET = "UTF-8"
        # client = self.getClient('ses', AWS_REGION)
        client = boto3.client('ses', region_name=AWS_REGION)
        try:
            response = client.send_email(
                Destination={
                    'ToAddresses': RECIPIENT,
                },
                Message={
                    'Body': {
                        'Html': {
                            'Charset': CHARSET,
                            'Data': BODY_HTML,
                        },
                        'Text': {
                            'Charset': CHARSET,
                            'Data': BODY_TEXT,
                        },
                    },
                    'Subject': {
                        'Charset': CHARSET,
                        'Data': SUBJECT,
                    },
                },
                Source=SENDER,
            )
        except Exception as e:
            print('email sent fail : '+str(e))
            return False
        else:
            print('email sent')
