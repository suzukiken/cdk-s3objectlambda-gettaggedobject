import boto3
import urllib.request
import urllib.parse
import os
import json
import datetime

def json_default_encode(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()

SEPARATER = urllib.parse.quote('@')
BUCKET_NAME = os.environ['BUCKET_NAME']
TAG_NAME = 'closed'

def lambda_handler(event, context):
    print(event)
    print(boto3.__version__)
    
    object_get_context = event["getObjectContext"]
    request_route = object_get_context["outputRoute"]
    request_token = object_get_context["outputToken"]
    s3_url = object_get_context["inputS3Url"]

    client = boto3.client('s3')
    
    url = urllib.parse.urlparse(s3_url)
    param = url.path[1:] # remove "/" for /index.txt@latest -> index.txt@latest
    
    if SEPARATER in param:
        splited = param.split(SEPARATER)
        key = '.'.join(splited[:-1])
        arg = splited[-1]
    else:
        key = param
        arg = None
    
    print(key)
    print(arg)
    
    if not arg:
        response = client.get_object(
            Bucket=BUCKET_NAME,
            Key=key,
        )
        client.write_get_object_response(
            Body=response['Body'].read().decode('utf8'),
            RequestRoute=request_route,
            RequestToken=request_token)
        
        return {'status_code': 200}

    # arg is like
    # 202001: tagged version
    # latest: latest tagged version
    # earliest: oldest tagged version

    first = True
    response = {}
    
    kargs = {
        'Bucket': BUCKET_NAME,
        'Prefix': key,
        'MaxKeys': 1000,
    }
    
    versions = []
    tags = {}
    
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
        response = client.get_object_tagging(
            Bucket=BUCKET_NAME,
            Key=key,
            VersionId=version['VersionId'],
        )
        
        print(response)
    
        for tag in response['TagSet']:
            if tag['Key'] == TAG_NAME:
                if not tag['Value'] in tags:
                    tags[tag['Value']] = []
                tags[tag['Value']].append({
                    'VersionId': version['VersionId'],
                    'LastModified': version['LastModified']
                })
    
    item = None
    
    sorted_versions = sorted(tags.items())
    
    if arg == 'log':
        client.write_get_object_response(
            Body=json.dumps(sorted_versions, default=json_default_encode),
            RequestRoute=request_route,
            RequestToken=request_token
        )
        return {'status_code': 200}

    # if same tag is found, selet latest.
    if arg == 'latest':
        item = sorted(sorted_versions[-1][1], key=lambda x:x['LastModified'])[-1]
    elif arg == 'earliest':
        item = sorted(sorted_versions[0][1], key=lambda x:x['LastModified'])[-1]
    elif arg in tags:
        item = sorted(tags[arg], key=lambda x:x['LastModified'])[-1]
    
    if not item:
        client.write_get_object_response(
            Body='no data',
            RequestRoute=request_route,
            RequestToken=request_token
        )
        return {'status_code': 200}
    
    response = client.get_object(
        Bucket=BUCKET_NAME,
        Key=key,
        VersionId=item['VersionId'],
    )
    
    client.write_get_object_response(
        Body=response['Body'].read().decode('utf8'),
        RequestRoute=request_route,
        RequestToken=request_token
    )
    return {'status_code': 200}