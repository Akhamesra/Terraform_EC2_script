from flask.cli import AppGroup
from Python_automation import list_handler
import shutil
import click
import boto3
import os
from pathlib import Path

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