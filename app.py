from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from flask import Flask, request
from dotenv import load_dotenv
import os
import json

load_dotenv()
app = Flask(__name__)

twilio = Client(os.getenv('TWILIO_SID'), os.getenv('TWILIO_TOKEN'))
forward_numbers = json.loads(os.getenv('FORWARD_NUMBERS'))

@app.route('/voice', methods = ['POST'])
def receive_voice():
  from_number = request.form['From']
  caller = getCallerId(from_number).capitalize()
  for forward_to in forward_numbers:
    twilio.messages.create(
      body = f'{caller} is at the gate calling from {from_number}',
      from_ = os.getenv('TWILIO_NUMBER'),
      to = forward_to
    )
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
  for forward_to in forward_numbers:
    twilio.messages.create(
      body = f'Gate Message from {caller} @ {from_number} \n{incoming_text}',
      from_ = os.getenv('TWILIO_NUMBER'),
      to = forward_to
    )
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