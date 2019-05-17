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
    # Get Cognito data and Put into Dynamo
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    table = dynamodb.Table("HekaCounselor")
    newCounselor = {}
    current_timestamp = datetime.datetime.now().isoformat()
    newCounselor["insertedAtTimestamp"] = current_timestamp
    usrAttr = event['request']['userAttributes']
    newCounselor['CounselorId'] = usrAttr['email']
    newCounselor['firstName'] = usrAttr['given_name']
    newCounselor['lastName'] = usrAttr['family_name']
    newCounselor['phoneNum'] = usrAttr['phone_number']
    newCounselor['skypeId'] = usrAttr['profile']
    newCounselor['gender'] = usrAttr['gender']
    response = table.put_item(Item=newCounselor)

    # And cache in Elasticsearch
    host = "https://search-cloud-final-iet672enwrhyanbedqvknoizeq.us-east-1.es.amazonaws.com"
    index = 'counselor'
    type = 'availability'
    did = usrAttr['email']
    document = {
        'counselorId': usrAttr['email'],
        'availability': 'offline'
    }
    endpoint = '{}/{}/{}/{}'.format(host, index, type, did)
    headers = {'Content-Type': 'application/json'}
    r = requests.post(endpoint, data=json.dumps(document), headers=headers)
    print(r.content)

    return event