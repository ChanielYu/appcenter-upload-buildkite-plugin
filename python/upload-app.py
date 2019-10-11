#!/usr/bin/env python3
import json
import requests
import argparse

'/Users/yuc/Development/TAB/android/android-TAB/TAB/build/outputs/apk/tabWebsite/debug/TAB-tab-website-debug.apk'

BASE_URL = 'https://api.appcenter.ms/v0.1/apps'
UPLOAD_URL = 'release_uploads'
HEADERS = {'Accept': 'application/json', 'Content-Type': 'application/json',
           'X-API-Token': '439d8f2e3db549553e2183ff7d627762351961c5'}
UPLOAD_FILE_NAME_KEY = 'ipa'
UPLOAD_FILE_CONTENT = 'TAB.apk'
OWNER_NAME = 'chaniel-yu'

release_information = {
    "release_id": 123,
    "build_version": "0.1",
    "build_number": "001"
}


def get_upload_url(owner, app, release_info, filename):
    params = json.dumps(release_info).encode()
    url = '/'.join([BASE_URL, owner, app, UPLOAD_URL])
    response = requests.post(url, data=params, headers=HEADERS)
    upload_data = json.loads(response.content.decode())
    print('Create upload resource status code:', response.status_code)
    # Upload
    multipart_form_data = {
        UPLOAD_FILE_NAME_KEY: (UPLOAD_FILE_CONTENT, open(filename, 'rb'))
    }
    upload_response = requests.post(upload_data['upload_url'], files=multipart_form_data)
    print('Upload resource status code:', upload_response.status_code)
    #  Patch
    patch_url = '/'.join([BASE_URL, owner, app, 'release_uploads', upload_data['upload_id']])
    payload = "{\"status\": \"committed\"}"
    patch_params = requests.patch(patch_url, data=payload, headers=HEADERS)
    print('Commit upload status code:', patch_params.status_code)


parser = argparse.ArgumentParser()
parser.add_argument("--appName", required=True, type=str)
parser.add_argument("--appFile", required=True, type=str)
args = parser.parse_args()
app_name = args.appName
app_file = args.appFile
print(app_name, app_file)
# get_upload_url(OWNER_NAME, app_name, release_information, app_file)
