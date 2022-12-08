import json
import logging
import os

import requests
from fastapi import FastAPI, HTTPException, Request

logger = logging.getLogger()
logger.setLevel(logging.INFO)

API_KEY = os.getenv('API_KEY')
SLACK_WEBHOOK = os.getenv('SLACK_WEBHOOK')

app = FastAPI()


@app.get('/')
async def catch_all_other():
    """
    Other catch all function for vercel

    :return:
    """
    return {'msg': 'Nothing here'}


@app.post('/webhook/slack/{api_key}')
async def webhook_slack(api_key: str, request: Request):
    """
    Endpoint receive sentry message and forward to Slack

    :param api_key:
    :param request:
    :return:
    """
    if api_key != API_KEY:
        raise HTTPException(status_code=404, detail="Project not found")

    msg = await request.body()
    message = json.loads(msg)

    '''
    {
     "webhook_setting_id": "12345",
     "webhook_event_type": "mention_to_me",
     "webhook_event_time": 1498028130,
     "webhook_event":{
     "from_account_id": 123456,
     "to_account_id": 1484814,
     "room_id": 567890123,
     "message_id": "789012345",
     "body": "[To:1484814]What do you like to eat？",
     "send_time": 1498028125,
     "update_time": 0
     }
    }
    '''
    msg_body = message['webhook_event']['body']
    room_id = message['webhook_event']['room_id']
    message_id = message['webhook_event']['message_id']
    full_url = f"https://www.chatwork.com/#!rid{room_id}-{message_id}"
    # Full link message https://www.chatwork.com/#!rid96550851-1652563248232267776

    slack_msg = {
        'text': f"{msg_body}\n\nLink: {full_url}"
    }

    try:
        r = requests.post(SLACK_WEBHOOK, json=slack_msg)

        # https://api.slack.com/messaging/webhooks#handling_errors
        r.raise_for_status()
    except Exception as e:
        logger.error(e)
        raise e
    # End slack

    # return slack_msg
    return {'msg': 'ok'}
