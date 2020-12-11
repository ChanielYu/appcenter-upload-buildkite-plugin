#!/usr/bin/env python3
import argparse
import json
import os
import requests

########################################################################################################################
# MASTER_TOKEN = '6f5093eb9a155f96cb2f97148172f923c0c575f5'
# PERSONAL_TOKEN = '439d8f2e3db549553e2183ff7d627762351961c5'
# owner_Name = 'The-Tabcorp-Mobile-Robot-Organization'
# appName = 'TAB-Android-Treble'
# releaseNotes = 'Test Release notes'
# owner_Name = 'chaniel-yu'
# appName = 'ChanielTest'
# appFile = \
#     '/Users/yuc/Development/TAB/android/android-TAB/TAB/build/outputs/apk/tabWebsite/debug/TAB-tab-website-debug.apk'
########################################################################################################################

ORGANIZATION_NAME = 'The-Tabcorp-Mobile-Robot-Organization'
DEFAULT_DISTRIBUTION_GROUP_NAME = 'Tabcorp-Mobile'
BASE_URL = 'https://api.appcenter.ms'
APP_URL = 'v0.1/apps'
ORG_URL = 'v0.1/orgs'
DISTRIBUTION_GROUPS_URL = 'distribution_groups'
UPLOAD_URL = 'uploads/releases'
HEADERS = {'Accept': 'application/json', 'Content-Type': 'application/json'}
UPLOAD_FILE_NAME_KEY = 'ipa'
UPLOAD_FILE_CONTENT = 'TAB.apk'

CLI_RELEASE = 'appcenter distribute release'
CLI_PARA_APP = '--app'
CLI_PARA_FILE = '--file'
CLI_PARA_GROUP = '--group'
CLI_PARA_NOTES = '--release-notes'
CLI_PARA_TOKEN = '--token'
CLI_PARA_QUIET = '--quiet'

release_information = {
    "release_id": 0
}


class AppCenter:
    def __init__(self, token: str, app_name: str, owner_name: str = ORGANIZATION_NAME):
        HEADERS['X-API-Token'] = token
        self.app_name = app_name
        self.owner_name = owner_name
        self.distribution_group_name = None
        self.distribution_group_id = None
        self.release_id = 0

    def setup_distribution(self, group_name: str = DEFAULT_DISTRIBUTION_GROUP_NAME):
        url = '/'.join([BASE_URL, ORG_URL, ORGANIZATION_NAME, DISTRIBUTION_GROUPS_URL])
        response = requests.get(url, headers=HEADERS)
        groups_data = json.loads(response.content.decode())
        distribution_group = next(item for item in groups_data if item['name'] == group_name)
        self.distribution_group_name = distribution_group['name']
        self.distribution_group_id = distribution_group['id']
        print('Distribute to %s group, group id = %s' % (self.distribution_group_name, self.distribution_group_id))
        url = '/'.join(
            [BASE_URL, ORG_URL, ORGANIZATION_NAME, DISTRIBUTION_GROUPS_URL, self.distribution_group_name, 'apps'])
        response = requests.get(url, headers=HEADERS)
        apps_data = json.loads(response.content.decode())
        in_group = any(item for item in apps_data if item['name'] == self.app_name)
        if not in_group:
            response = requests.post(url, json={'apps': [{'name': self.app_name}]}, headers=HEADERS)
            print('App added into group %s: status = %d' % (self.distribution_group_name, response.status_code))
        else:
            print('Already in %s group' % self.distribution_group_name)

    def upload_app(self, release_info, filename):
        params = json.dumps(release_info).encode()
        url = '/'.join([BASE_URL, APP_URL, self.owner_name, self.app_name, UPLOAD_URL])
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
        patch_url = '/'.join(
            [BASE_URL, APP_URL, self.owner_name, self.app_name, 'release_uploads', upload_data['upload_id']])
        payload = "{\"status\": \"committed\"}"
        patch_params = requests.patch(patch_url, data=payload, headers=HEADERS)
        print('Commit upload status code:', patch_params.status_code)

    def release_app(self, release_notes='Release'):
        url = '/'.join([BASE_URL, APP_URL, self.owner_name, self.app_name, 'releases'])
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            releases = json.loads(response.content.decode())
            self.release_id = max(releases, key=compare_key)['id']
            url = '/'.join([BASE_URL, APP_URL, self.owner_name, self.app_name, 'releases', '%d' % self.release_id])
            response = requests.put(url, json={'release_notes': release_notes}, headers=HEADERS)
            print('Release id=%d app name= %s to %s status_code=%d' %
                  (self.release_id, self.app_name, self.distribution_group_name, response.status_code))
            url = '/'.join(
                [BASE_URL, APP_URL, self.owner_name, self.app_name, 'releases', '%d' % self.release_id, 'groups'])
            response = requests.post(url, json={
                'id': self.distribution_group_id,
                'mandatory_update': False,
                'notify_testers': True
            }, headers=HEADERS)
            print('Distributes a release to %s group status code = %d' %
                  (self.distribution_group_name, response.status_code))

    def release_by_cli(self, filename, release_notes='Release'):
        cli_app_name = '/'.join([self.owner_name, self.app_name])
        command = ' '.join(
            [CLI_RELEASE, CLI_PARA_QUIET, CLI_PARA_APP, cli_app_name,
             CLI_PARA_FILE, filename,
             CLI_PARA_GROUP, self.distribution_group_name,
             CLI_PARA_NOTES, '\"' + release_notes + '\"',
             CLI_PARA_TOKEN, HEADERS['X-API-Token']])
        print('running command: %s' % command)
        os.system(command)


def compare_key(item):
    return item['id']


parser = argparse.ArgumentParser()
parser.add_argument("--appToken", required=True, type=str)
parser.add_argument("--appName", required=True, type=str)
parser.add_argument("--appFile", required=True, type=str)
parser.add_argument("--releaseNotes", required=True, type=str)
args = parser.parse_args()
appToken = args.appToken
appName = args.appName
appFile = args.appFile
releaseNotes = args.releaseNotes

appCenter = AppCenter(appToken, appName, 'chaniel-yu')
appCenter.setup_distribution()
appCenter.release_by_cli(appFile, releaseNotes)
