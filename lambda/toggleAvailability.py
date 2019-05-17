import json
import datetime
import time
import os
import dateutil.parser
import logging
import boto3

from botocore.vendored import requests

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def lambda_handler(event, context):
    logger.debug(event)

    # And cache in Elasticsearch
    host = "https://search-cloud-final-iet672enwrhyanbedqvknoizeq.us-east-1.es.amazonaws.com"
    index = 'counselor'
    type = 'availability'
    did = event['counselorId']
    document = {
        'counselorId': did,
        'availability': event['statusToSet']
    }
    endpoint = '{}/{}/{}/{}'.format(host, index, type, did)
    headers = {'Content-Type': 'application/json'}
    r = requests.post(endpoint, data=json.dumps(document), headers=headers)
    # print(r.content)

    return {
        'statusCode': 200,
        'body': 'Hello'
    }