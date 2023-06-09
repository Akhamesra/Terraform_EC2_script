from flask.cli import AppGroup
import click
import boto3
import config.settings as AppSetting
import json
from botocore.exceptions import ClientError
import os

def getClient(aws_profile):
    session = boto3.session.Session(profile_name = aws_profile)
    client = session.client('ses')
    return client

ses = AppGroup('ses')

@ses.command('sendLaunchMail')
@click.option('--number_of_ec2')
@click.option('--aws_profile',  required=True, default='default', help='AWS session profile')
def sendLaunchMail(number_of_ec2,aws_profile):  
        RECIPIENTS=AppSetting.recipients     
        # if(email.find('$$')!=-1):
        #     RECIPIENT=email.split('$$')  
        SENDER = AppSetting.sender['name'] + " <" + AppSetting.sender['email'] + ">"
        AWS_REGION = "ap-south-1"
        SUBJECT = "Instances Created"
        BODY_TEXT = "FROM TEAM SRE"
        BODY_HTML = number_of_ec2+" EC2 instances created."
        CHARSET = "UTF-8"
        # client = self.getClient('ses', AWS_REGION)
        
        client = getClient(aws_profile)
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
@click.option('--aws_profile',  required=True, default='default', help='AWS session profile')
def sendTerminateMail(aws_profile):
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
        client = getClient(aws_profile)
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
