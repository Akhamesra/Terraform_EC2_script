from flask.cli import AppGroup
import click
import boto3
import config.settings as AppSetting
import json
from botocore.exceptions import ClientError
import os
from os import path
from botocore.config import Config

def getResource(aws_profile):
    session = boto3.session.Session(profile_name = aws_profile)
    resource = session.resource('s3')
    return resource

s3 = AppGroup('s3')

@s3.command('downloadFile')
@click.option('--aws_profile',  required=True, default='default', help='AWS session profile')
def downloadFile(aws_profile):
    bucketname = AppSetting.bucketname
    objectname_number = AppSetting.objectnumber['paths3']+AppSetting.objectnumber['name'] #S3/path/number
    objectpath_number = AppSetting.objectnumber['pathlocal'] +AppSetting.objectnumber['name'] #local/path/number
    try:
        s3_resource = getResource(aws_profile)
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
    bucketname = AppSetting.bucketname
    url = boto3.client('s3').generate_presigned_url(
                                        ClientMethod='get_object',
                                        Params={
                                            'Bucket': bucketname,
                                            'Key': key
                                        },
                                        ExpiresIn=21600
                                    )
    print(url)
@s3.command('uploadFile')
@click.option('--aws_profile',  required=True, default='default', help='AWS session profile')
def uploadFile(aws_profile):
    try:
        bucketname = AppSetting.bucketname #S3 name

        objectname_number = AppSetting.objectnumber['paths3']+AppSetting.objectnumber['name'] #S3/path/number
        objectpath_number = AppSetting.objectnumber['pathlocal'] +AppSetting.objectnumber['name'] #local/path/number
        increamentbatch(objectpath_number)

        objectname_ip = AppSetting.objectip['paths3']+AppSetting.objectip['name'] #S3/path/instances_ips.txt
        objectpath_ip = AppSetting.objectip['pathlocal'] +AppSetting.objectip['name'] #local/path/instances_ips.txt

        s3_resource = getResource(aws_profile)
        s3_resource.Object(bucketname,objectname_number).upload_file(objectpath_number)
        s3_resource.Object(bucketname,objectname_ip).upload_file(objectpath_ip)
        print('Files Uploaded')
        getUrl(objectname_ip)
    except Exception as ce:
        print(ce)

@s3.command('deleteFile')
@click.option('--aws_profile',  required=True, default='default', help='AWS session profile')
def deleteFile(aws_profile):
        try:
            bucketname = AppSetting.bucketname
            objectname_number = AppSetting.objectnumber['paths3']+AppSetting.objectnumber['name'] #S3/path/number
            objectname_ip = AppSetting.objectip['paths3']+AppSetting.objectip['name'] #S3/path/instances_ips.txt
            
            s3_resource = getResource(aws_profile)
            s3_resource.Object(bucketname, objectname_number).delete()
            print('next_batch_number file deleted')
            s3_resource.Object(bucketname, objectname_ip).delete()

            if path.exists(AppSetting.objectip['pathlocal']+AppSetting.objectip['name']):
                os.remove(AppSetting.objectip['pathlocal']+AppSetting.objectip['name'])
                print('instance_ips file deleted')

        except ClientError as ce:
            print(f"{ce.response['Error']['Code']} : {ce.response['Error']['Message']}")
