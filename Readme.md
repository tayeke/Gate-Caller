# Gate Caller Service

This app uses twilio voice service to negotiate an incoming call from a number that is not your personal number.

This app was designed to solve a gate/door access scenario where you want to publicly post a phone number for someone to request access through a gate. We want the posted number to not be our personal number, but ultimately recieve the call on a personal number.

We also want to know the incoming call was from the gate and not a spam call from an unknown number with caller id.

Bonus we want to send a pre-emptive text message before the call so we log that someone was at the gate and possibly any other meta info from the twilio call record.

Some people might mistakenly text the application so we will need to simply forward any text messages.

## Test Locally

You can easily run this flask app locally if you have Docker, but running `docker-build up`. The app is available on port *5000*.

Remember to set up your .env file by copying the .env.example and filling in your details.

You're going to need to run ngrok locally to point the twilio services to your local app `ngrok http http://localhost:5000`.

## Setup Cloudbuild

- Install gcloud cli
- Your .env file will be used for the build, the production environment variable is set by the cloudbuild task.
- Start a new app deployment with `gcloud submit build` from the main directory.
  - You may run into roadblocks with configuring google cloud service accounts, just follow the prompts if this is your first time.
- The cloud run service will be private to iam users and service accounts with the cloud run invoke role. You can follow these steps to get a bearer token for your connection to the app.
  - Go to iam in GCP
  - Go to service accounts
  - Create new service account (name it twilio) and provide the permission to invoke cloud run.
  - Click on the options for the SA and select manage keys. Proceed to create a JSON key.
  - Back on your computer use gcloud cli to init the SA and get it's token.
    - `gcloud auth activate-service-account twilio@[PROJECT_ID].iam.gserviceaccount.com --key-file=/Users/[YOU]/Downloads/[KEYFILE].json`
    - `gcloud auth print-identity-token twilio@[PROJECT_ID].iam.gserviceaccount.com`

## Setup Twilio

Create a new TwiML app under the voice service in twilio. Copy the base URL as either your cloud run endpoint or your ngrok https endpoint.

- Voice Configuration: `[BASE_URL]/voice` [http POST]
- Messaging Configuration: `[BASE_URL]/sms` [http POST]

Find your receiving phone number in twilio and set the 'configure with' to be TwiML app and then pick the app you just configured.