'''
    LF0
'''

import json
import boto3

from botocore.vendored import requests
from collections import defaultdict

from boto3.dynamodb.conditions import Key, Attr

STOP_WORDS = set(['what', 'was', 'doesn', 'couldn', "didn't", 'nor', 'from', 'further', 'above', 'me', 'y', "should've", 'as', 'yours', 'she', 'didn', 'more', 'ourselves', "she's", 'haven', 'themselves', 'by', "won't", 'we', "isn't", 'will', 'its', 'again', 'shouldn', 'be', 'he', 'his', 'to', 'when', "wasn't", "don't", 'is', 'once', "needn't", "wouldn't", 'some', 'itself', 'did', 'isn', 'here', 'off', 'been', 'such', 'wouldn', 'where', 'few', 'an', "you'd", 'myself', 'no', 'hadn', 'each', 'not', "shan't", 'being', 'own', 'our', 'just', 'yourselves', 'her', 'doing', 'herself', 'does', 'before', 'these', 'up', 'this', 'most', 's', "mightn't", 'a', 'only', 'over', 'aren', 'so', 'won', 't', 'm', 'mightn', 'having', 'then', 'theirs', 'do', 'against', 'of', 'it', 'in', 'on', 'or', 'both', 'my', 'about', 'those', 'll', 'if', "haven't", "weren't", 'their', "it's", 'have', 'ain', 'whom', 'and', 'there', 'your', 've', 'you', 'yourself', 'because', 'can', 'than', 'for', 'that', 'has', 'any', 'd', 'while', 'but', 'during', "shouldn't", 'into', "hasn't", 'who', 'needn', "doesn't", "hadn't", 'were', 'through', "aren't", "you'll", 'him', 'all', 'wasn', 'ours', 'below', 'mustn', "mustn't", 'between', "that'll", "couldn't", 'hasn', "you're", 'too', "you've", 'same', 'hers', 'they', 'down', 'the', 'don', 'i', 'are', 'should', 'them', 'which', 'ma', 'himself', 'under', 'after', 'why', 'how', 'other', 'shan', 'o', 'at', 'had', 'out', 'weren', 'now', 'am', 'until', 'very', 'with', 'r'])
RELATIONSHIP_WORDS = set(['friend', 'date', 'break', 'clique', 'groupmate', 'classmate', 'group', 'people', 'person'])
FINANCE_WORDS = set(['money', 'spending', 'budget', 'broke', 'cheap', 'expensive', 'pricey', 'investment'])
FAMILY_WORDS = set(['divorce', 'parents', 'parent', 'siblings', 'brother', 'sister', 'stepbrother', 'stepsister', 'halfbrother', 'halfsister', 'aunt', 'uncle', 'grandfather', 'grandmother'])
SCHOOL_WORDS = set(['grades', 'professor', 'assignment', 'homework', 'midterm'])

def try_ex(func):
    try:
        return func()
    except KeyError:
        return None

def determine_problem(keyPhrases):
    rawKP = [k['Text'].lower() for k in keyPhrases]

    print(rawKP)

    cleanKP = []
    for r in rawKP:
        for rr in r.split(' '):
            if rr not in STOP_WORDS:
                cleanKP.append(rr)

    print(cleanKP)

    problem_cnt = defaultdict(int)
    for c in cleanKP:
        if c in RELATIONSHIP_WORDS:
            problem_cnt['friendship/relationship'] += 1
        elif c in FINANCE_WORDS:
            problem_cnt['finance'] += 1
        elif c in FAMILY_WORDS:
            problem_cnt['family'] += 1
        elif c in SCHOOL_WORDS:
            problem_cnt['school'] += 1
        else:
            problem_cnt['other'] += 1

    print(problem_cnt)

    maxTopic = None
    maxCnt = -1
    for k, v in problem_cnt.items():
        if k != 'other' and v > maxCnt:
            maxTopic, maxCnt = k, v/len(cleanKP)

    return {
        'understoodProblem': maxTopic,
        'confidence': maxCnt,
        'parsedKeywords': cleanKP
    }

def close(session_attributes, message):
    closeBody = {
        'sessionAttributes': session_attributes,
        'response': message
    }
    return {
        'statusCode': 200,
        'body': closeBody
    }

def lambda_handler(event, context):
    mainResponse = {
      "text": "",
      "sessionAttributes": {
        "currentProblem": ""
      },
      "dialogState": "",
      "counselorEmail": ""
    }
    session_attributes = event['sessionAttributes'] if event['sessionAttributes'] is not None else {}
    rawProblemText = event['text']

    # TODO: Query elasticsearch for available counselor
    # TODO: Query dynamo to fetch skypeId
    # Use Lex to disambiguate query
    client = boto3.client('lex-runtime')
    response = client.post_text(
        botName = 'CareBot',
        botAlias = '$LATEST',
        userId = 'escalateUser',
        inputText = rawProblemText
    )
    if response['dialogState'] == 'ReadyForFulfillment':
        query = 'https://search-cloud-final-iet672enwrhyanbedqvknoizeq.us-east-1.es.amazonaws.com/counselor/availability/_search'
        headers = {'Content-Type': 'application/json'}
        q = {"query": {"match": {"availability": "online"}}}
        r = requests.post(query, headers=headers, data=json.dumps(q))
        data = json.loads(r.content.decode('utf-8'))
        print(data)
        hits = data['hits']
        if hits['total'] > 0:
            cEmail = hits['hits'][0]['_id']
            mainResponse['response'] = 'I found an available counselor for you. '

            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table('HekaCounselor')
            result = table.scan(FilterExpression=Attr('CounselorId').eq(cEmail))
            skypeId = result['Items'][0]['skypeId']
            # return result
            mainResponse['counselorEmail'] = skypeId
        else:
            # TODO: SNS counselors to go online
            pass
    else:
        # Chain problem description for accurate comprehension
        session_attributes['currentProblem'] = ' '.join([session_attributes['currentProblem'], rawProblemText])
        currentProblemText = session_attributes['currentProblem']
        mainResponse['sessionAttributes'] = session_attributes

        # Invoke AWS Comprehend
        comprehendResponse = None
        comprehendClient = boto3.client('comprehend')
        keyPhraseResponse = comprehendClient.detect_key_phrases(
                Text = currentProblemText,
                LanguageCode = 'en'
            )
        determinedRes = determine_problem(keyPhraseResponse['KeyPhrases'])

        sentimentResponse = comprehendClient.detect_sentiment(
                Text = currentProblemText,
                LanguageCode = 'en'
            )
        if sentimentResponse['Sentiment'] == 'NEGATIVE' and determinedRes['understoodProblem']:
            mainResponse['comprehension'] = {
                'understoodProblem': determinedRes['understoodProblem'],
                'confidence': determinedRes['confidence'],
                'sentiment': sentimentResponse['Sentiment']
            }
            mainResponse['response'] = 'It seems like you are facing a problem with %s. ' % determinedRes['understoodProblem']
        else:
            return close(session_attributes, 'Can you please describe more?')

        keywords = determinedRes['parsedKeywords']
        keywords.append(determinedRes['understoodProblem'])
        print(keywords)
        # Query elasticsearch for article
        query = 'https://search-cloud-final-iet672enwrhyanbedqvknoizeq.us-east-1.es.amazonaws.com/doc/_search'
        headers = {'Content-Type': 'application/json'}
        prepared_q = []
        for k in keywords:
            prepared_q.append({"term": {"article.content": k}})
        q = {"query": {"bool": {"should": prepared_q}}}
        r = requests.post(query, headers=headers, data=json.dumps(q))
        data = json.loads(r.content.decode('utf-8'))
        # return data
        if data['hits']['total'] > 0:
            firstMatch = data['hits']['hits'][0]
            articleTitle = firstMatch['_source']['article']['title']
            articleAbstract = firstMatch['_source']['article']['abstract']
            articleContent = firstMatch['_source']['article']['content']
            mainResponse['response'] += 'I found an article titled "%s". It writes, "%s".' % (articleTitle, articleAbstract)
            mainResponse['fullArticle'] = articleContent
            # return articleTitle, articleAbstract, articleContent

    return {
        'statusCode': 200,
        'body': mainResponse
    }