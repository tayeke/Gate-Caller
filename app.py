from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from flask import Flask, request
from dotenv import load_dotenv
import os
import json
import requests
import pathlib
print("ENV exists?", pathlib.Path('.env').exists())
print("FORWARD_NUMBERS=", os.getenv('FORWARD_NUMBERS'))

load_dotenv()
app = Flask(__name__)

twilio = Client(os.getenv('TWILIO_SID'), os.getenv('TWILIO_TOKEN'))
forward_numbers = json.loads(os.getenv('FORWARD_NUMBERS', '[]'))
notification_method = os.getenv('NOTIFICATION_METHOD', 'sms')
ntfy_topics = json.loads(os.getenv('NTFY_TOPICS', '[]'))

@app.route('/voice', methods = ['POST'])
def receive_voice():
  sendVoiceNotifications()

  response = VoiceResponse()
  response.say(os.getenv('WELCOME_MESSAGE'), voice='man')
  response.pause(length=2)

  for forward_to in forward_numbers:
    response.dial(forward_to)

  return str(response)

@app.route('/sms', methods = ['POST'])
def receive_sms():
  from_number = request.form['From']
  incoming_text = request.form['Body']
  caller = getCallerId(from_number)

  sendNotifications(f'Gate Message from {caller} @ {from_number} \n{incoming_text}')

  return 'success'

def getCallerId(from_number: str) -> str:
  try:
    lookup = twilio.lookups.v1 \
      .phone_numbers(from_number) \
      .fetch(type=['caller-name'])
    caller = lookup.caller_name['caller_name']
    if caller == None: caller = 'someone'
  except:
    caller = 'someone'
  return caller

def sendVoiceNotifications():
  from_number = request.form['From']
  caller = getCallerId(from_number).capitalize()
  sendNotifications(f'{caller} is at the gate calling from {from_number}')

def sendNotifications(message: str):

  for forward_to in forward_numbers:
    match notification_method:

      case 'sms':
        twilio.messages.create(
          body = message,
          from_ = os.getenv('TWILIO_NUMBER'),
          to = forward_to
        )

      case 'ntfy':
        for topic in ntfy_topics:
          requests.post(
            f'https://ntfy.sh/{topic}',
            data=message.encode(encoding='utf-8'),
            headers={
              'Title': 'Gate Caller',
              'Priority': 'urgent',
            }
          )