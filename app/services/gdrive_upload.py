from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os

FOLDER_ID = "138q20HHJFDxrQ87t5fVf-nOBYqc5jJxf"

# Absolute paths
CRED_DIR = os.path.dirname(__file__)
CLIENT_SECRETS = os.path.join(CRED_DIR, "client_secrets.json")
CREDENTIALS_FILE = os.path.join(CRED_DIR, "credentials.json")


def authenticate_drive():
    gauth = GoogleAuth()
    gauth.settings['client_config_file'] = CLIENT_SECRETS
    gauth.LoadCredentialsFile(CREDENTIALS_FILE)

    if gauth.credentials is None:
        raise Exception("No valid credentials found.")
    elif gauth.access_token_expired:
        gauth.Refresh()
        gauth.SaveCredentialsFile(CREDENTIALS_FILE)
    else:
        gauth.Authorize()

    return GoogleDrive(gauth)


def upload_to_drive(file_path, filename, folder_id=FOLDER_ID):
    drive = authenticate_drive()
    file = drive.CreateFile({
        "title": filename,
        "parents": [{"id": folder_id}]
    })
    file.SetContentFile(file_path)
    file.Upload()
    return f"https://drive.google.com/uc?export=view&id={file['id']}"
