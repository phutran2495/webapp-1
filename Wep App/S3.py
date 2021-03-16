import logging
import boto3
from botocore.exceptions import ClientError
import os

s3bucket = os.environ.get('bucketname')

s3_client = boto3.client('s3')

def upload_file(file, bucketname= s3bucket, object_name=None):
    try:
        response = s3_client.put_object(Body=file, Bucket=bucket, Key=object_name)
        return True
    except ClientError as e:
        return False


def delete_file(bucket_name = s3bucket, key):
    try:
        response = s3_client.delete_object(
            Bucket=bucket_name,
            Key=key,
        )
        return True
    except:
        return False

