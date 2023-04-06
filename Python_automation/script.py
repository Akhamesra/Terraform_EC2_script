from flask.cli import AppGroup
import click
import boto3
import config.settings as AppSetting

s3_resource = boto3.resource('s3')

s3 = AppGroup('s3')

@s3.command('downloadFile')
def downloadFile():
    bucketname = AppSetting.bucketname
    objectpath = AppSetting.batchNumber['path']
    objectname = AppSetting.batchNumber['name']
    try:
        s3_resource.Object(bucketname,objectname).download_file(objectpath)
        print('Downloaded')
    except Exception as ce:
        print(ce)

@s3.command('uploadFile')
def uploadFile():
    try:
        bucketname = AppSetting.bucketname
        objectpath = AppSetting.batchNumber['path']
        objectname = AppSetting.batchNumber['name']
        with open(objectpath, "r") as f:
            number = int(f.read())
        number += 1
        with open(objectpath, "w") as f:
            f.write(str(number))
    
        s3_resource.Object(bucketname,objectname).upload_file(objectpath, ExtraArgs={'ACL':'public-read'})
        print('Upload succeeded')
    except Exception as ce:
        print(ce)

ses = AppGroup('SES')

@ses.command('sendMail')
@click.option('--email',required=True,help="Enter Sender's email id")
@click.option('--number_of_ec2')
def sendMail(email,number_of_ec2):  
        RECIPIENT=[email]      
        if(email.find('$$')!=-1):
            RECIPIENT=email.split('$$')  
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