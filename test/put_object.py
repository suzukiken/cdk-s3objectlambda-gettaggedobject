import boto3
import time
import os

client = boto3.client('s3')

BUCKET_NAME = os.environ.get('BUCKET_NAME')
KEY_NAME = 'index.txt'
TAG_NAME = 'closed'

varsions = [
    { 'body': 'あ' },
    { 'body': 'い' },
    { 'body': 'う', 'tag': '202104' },
    { 'body': 'え' },
    { 'body': 'お' },
    { 'body': 'か', 'tag': '202103' },
    { 'body': 'き', 'tag': '202102' },
    { 'body': 'く' },
    { 'body': 'け', 'tag': '202102'},
    { 'body': 'こ' },
    { 'body': 'さ' },
    { 'body': 'し' },
    { 'body': 'す', 'tag': '202103' },
    { 'body': 'せ' }
]

kwargs = {
    'Bucket': BUCKET_NAME,
    'Key': KEY_NAME,
}

for varsion in varsions:
    
    kwargs['Body'] = varsion['body']
    
    if 'tag' in varsion:
        kwargs['Tagging'] = '{}={}'.format(TAG_NAME, varsion['tag'])
    else:
        kwargs.pop('Tagging', None)
    
    time.sleep(1)
    
    response = client.put_object(**kwargs)
    
    print(response)