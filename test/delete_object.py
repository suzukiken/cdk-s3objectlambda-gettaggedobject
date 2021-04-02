import boto3
import os

client = boto3.client('s3')

BUCKET_NAME = os.environ.get('BUCKET_NAME')
KEY_NAME = 'index.txt'

first = True
response = {}

kargs = {
    'Bucket': BUCKET_NAME,
    'Prefix': KEY_NAME,
    'MaxKeys': 1000,
}

versions = []

while True:
    if first:
        first = False
    elif response['IsTruncated']:
        kargs.update({
            'KeyMarker': response['NextKeyMarker'],
            'VersionIdMarker': response['NextVersionIdMarker'],
        })
    else:
        break
    
    response = client.list_object_versions(**kargs)
    
    if 'Versions' in response:
        for version in response['Versions']:
            versions.append({
                'VersionId': version['VersionId'],
                'LastModified': version['LastModified'],
                'IsLatest': version['IsLatest'],
            })
    
for version in versions:
    response = client.delete_object(
        Bucket=BUCKET_NAME,
        Key=KEY_NAME,
        VersionId=version['VersionId'],
    )
    print(response)