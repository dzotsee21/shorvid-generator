import os
import google_auth_oauthlib.flow
import google.auth.transport.requests
import googleapiclient.discovery
import googleapiclient.http
import pickle
import yaml


with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)


SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_FILE = 'static/token.pickle'
CLIENT_SECRETS_FILE = config['google-secret-file-path']

def authenticate_youtube():
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    creds = None

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server()

        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    youtube = googleapiclient.discovery.build(
        "youtube", "v3", credentials=creds)

    return youtube


def upload_video(youtube, filename, title, description, tags):
    request_body = {
        "snippet": {
            "categoryId": "22",
            "title": title,
            "description": description,
            "tags": tags
        },
        "status":{
            "privacyStatus": "public"
        }
    }

    media_file = f"static/temp/videos/{filename}.mp4"

    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=googleapiclient.http.MediaFileUpload(media_file, chunksize=-1, resumable=True)
    )

    response = None 

    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload {int(status.progress()*100)}%")

        print(f"Video uploaded with ID: {response['id']}")
