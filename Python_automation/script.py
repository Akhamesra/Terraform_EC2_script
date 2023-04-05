from flask.cli import AppGroup

import shutil
import click
import boto3
import os
from pathlib import Path
from pathlib import Path


s3_resource = boto3.resource('s3')

s3 = AppGroup('s3')

@s3.command('downloadFile')
def downloadFile(bucketname='akshitkhamesraautomation'):
    objectpath = 'terraform_modules/EC2/number'
    object_name = 'number'
    try:
        s3_resource.Object(bucketname,object_name).download_file(objectpath)
        print('Downloaded')
    except Exception as ce:
        print(ce)

@s3.command('uploadFile')
def uploadFile(bucketname="akshitkhamesraautomation"):
    with open("terraform_modules/EC2/number", "r") as f:
        number = int(f.read())
    number += 1
    with open("terraform_modules/EC2/number", "w") as f:
        f.write(str(number))
    objectpath="terraform_modules/EC2/number"
    object_name = 'number'
    try:
        s3_resource.Object(bucketname,object_name).upload_file(objectpath, ExtraArgs={'ACL':'public-read'})
        print('Upload succeeded')
    except Exception as ce:
        print(ce)

# @s3.command('downloadFile')
# @click.option('--id',required=True)
# def download_object(id,bucketname="terraformkhamesra"):
#     objectpath = 'terraform_modules/EC2/terraform.tfstate'
#     object_name = 'tfstate_files/terraform'+id+'.tfstate'
#     try:
#         s3_resource.Object(bucketname,object_name).download_file(objectpath)
#         print('Download succeeded')
#     except Exception as ce:
#         print(f"{ce.response['Error']['Code']} : {ce.response['Error']['Message']}")


ses = AppGroup('SES')

@ses.command('sendMail')
@click.option('--email',required=True,help="Enter Sender's email id")
@click.option('--number_of_ec2')
def sendMail(email,number_of_ec2):  
        RECIPIENT=[email]      
        if(email.find('$$')!=-1):
            RECIPIENT=email.split('$$')  
        SENDER = 'Akshit <akhamesra31@gmail.com>'
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