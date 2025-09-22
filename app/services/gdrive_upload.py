import os
import shutil
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

FOLDER_ID = "138q20HHJFDxrQ87t5fVf-nOBYqc5jJxf"


# Directory where secret files are mounted on Render
CRED_DIR = os.environ.get("CRED_DIR", "/etc/secrets")
CLIENT_SECRETS = os.path.join(CRED_DIR, "client_secrets.json")
CREDENTIALS_FILE_SYMLINK = os.path.join(CRED_DIR, "credentials.json")
CREDENTIALS_FILE_TMP = "/tmp/credentials.json"  # writable copy for PyDrive

# Copy symlink to a real temp file
if os.path.exists(CREDENTIALS_FILE_SYMLINK):
    shutil.copy(CREDENTIALS_FILE_SYMLINK, CREDENTIALS_FILE_TMP)


def authenticate_drive():
    gauth = GoogleAuth()
    gauth.settings['client_config_file'] = CLIENT_SECRETS
    gauth.LoadCredentialsFile(CREDENTIALS_FILE_TMP)  # load the temp copy

    if gauth.credentials is None:
        raise Exception("No valid credentials found.")
    elif gauth.access_token_expired:
        gauth.Refresh()
        gauth.SaveCredentialsFile(CREDENTIALS_FILE_TMP)
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
