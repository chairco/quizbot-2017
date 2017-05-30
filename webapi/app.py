#!/usr/bin/env python

from flask import Flask
from flask import abort
from flask import request

import requests

try:
    from env import PAGE_TOKEN, FB_MESSENGER_URI, BOT_TOKEN
except Exception as e:
    from .env import PAGE_TOKEN, FB_MESSENGER_URI, BOT_TOKEN


app = Flask(__name__)

FB_MESSENGER_URI = FB_MESSENGER_URI + PAGE_TOKEN


def send_template_message(user_id, elements):
    data = {
        "recipient":{
            "id": user_id
        },
        "message":{
            "attachment": {
                "type":"template",
                "payload":{
                    "template_type":"generic",
                    "elements": elements
                }
            }
        }
    }

    r = requests.post(FB_MESSENGER_URI, json=data)
    if r.status_code != requests.codes.ok:
        print(r.content)


def send_text(reply_token, text, answers):
    data = {
        "recipient": {"id": reply_token},
        "message": {"text": text}
    }
    if answers:
        data["message"]["quick_replies"] = answers
    r = requests.post(FB_MESSENGER_URI, json=data)
    if r.status_code != requests.codes.ok:
        print(r.content)


def fb_post_handler(req):
    print(req.get_data())
    resp_body = req.get_json()

    for entry in resp_body["entry"]:
        for msg in entry["messaging"]:
            sender = msg['sender']['id']
            if 'message' in msg:
                if msg['message'].get('is_echo'):
                    return ""
                if 'text' not in msg['message']:
                    return ""
                if 'quick_reply' in msg['message']:
                    reply = msg["message"]["quick_reply"]
                    if reply['payload'] == "QUERY_CURRENCY":
                        send_text(sender, "This function is not worked yet.", None)
                    elif reply['payload'] == "CANCEL":
                        send_text(sender, "No problem.", None)
                    return ""
                text = msg['message']['text']
                if text == "btcusd":
                    element = [{
                        "title":"BTC - USD",
                        "image_url":"https://www.google.com/finance/chart?biw=696&bih=775&q=CURRENCY:BTCUSD&tkr=1&p=5Y&chst=vkc&chs=267x94",
                        "subtitle":"The currency between BTC and USD",
                        "buttons": [
                            {"type": "web_url",
                             "url": "https://btc-e.com/exchange/btc_usd",
                             "title": "View in BTC-E"
                             },
                            {"type": "postback",
                             "payload": "HAHAHA",
                             "title": "Laugh"
                             }
                        ]
                    }]
                    send_template_message(sender, element)
                elif text == "Btc":
                    send_text(sender, "Query currency?", [
                        {"content_type":"text",
                         "title":"Yes",
                         "payload":"QUERY_CURRENCY"
                         },
                        {"content_type":"text",
                         "title":"No",
                         "payload":"CANCEL"
                         }
                    ])
                else:
                    send_text(sender, text, None)
            elif 'postback' in msg:
                if msg['postback']['payload'] == "GET_STARTED":
                    send_text(sender, 'welcome', None)
                elif msg['postback']['payload'] == "HAHAHA":
                    send_text(sender, 'hahaha!', None)
    return ""


@app.route("/api/fb_webhook", methods=['GET', 'POST'])
def fb_cb_handler():
    if request.method == 'GET':
        token = request.args.get('hub.verify_token')
        if token == BOT_TOKEN:
            return request.args.get('hub.challenge')
        else:
            abort(403)
    elif request.method == 'POST':
        return fb_post_handler(request)
    else:
        abort(405) 


@app.route("/version", methods=['GET'])
def version():
    if request.method == 'GET':
       return "0.1"
    else:
        abort(404)


if __name__ == "__main__":
    app.run(port=5000)

