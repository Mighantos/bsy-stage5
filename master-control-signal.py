import sys
import requests
import json


class Git:

    def __init__(self, github_gist_api, api_token):
        self.GITHUB_GIST_API = github_gist_api
        self.API_TOKEN = api_token
        self.gist_id = ""

    def create_gist(self, gist_name):
        headers = {'Authorization': 'token %s' % self.API_TOKEN}
        params = {'scope': 'gist'}
        payload = {"description": "GIST created by python code",
                   "public": False,
                   "files": {gist_name: {"content": "Hello droids!"}}}

        res = requests.post(self.GITHUB_GIST_API, headers=headers, params=params, data=json.dumps(payload))
        if res.status_code != 201:
            print("Unable to create gist. Statu code " + str(res.status_code))
            exit(2)

        self.gist_id = json.loads(res.text)['id']

    def get_and_set_gist_id(self, gist_name):
        headers = {'Authorization': 'token %s' % self.API_TOKEN}
        params = {'Accept': 'application/vnd.github+json'}

        res = requests.get(self.GITHUB_GIST_API, headers=headers, params=params)

        if res.status_code != 200:
            print("Unable to get all gists. Statu code " + str(res.status_code))

        last_updated = ""
        for gist in json.loads(res.text):
            if gist_name in gist['files'].keys():
                if last_updated == "" or gist['updated_at'] > last_updated:
                    last_updated = gist['updated_at']
                    self.gist_id = gist['id']
        if self.gist_id == "":
            print("Unable to find gist " + gist_name + ".")
            exit(2)
        print("Using gist with id: " + self.gist_id)

    def update_gist(self, file_name, content):
        headers = {'Authorization': 'token %s' % self.API_TOKEN}
        params = {'scope': 'gist'}
        payload = {"description": "GIST updated by python code",
                   "public": False,
                   "files": {file_name: {"content": content}}}
        url = self.GITHUB_GIST_API + "/" + self.gist_id

        res = requests.post(url, headers=headers, params=params, data=json.dumps(payload))

        print(res.status_code)
        print(res.url)
        print(res.text)


if __name__ == '__main__':
    if (len(sys.argv) != 3):
        print("Program requires arguments:\nGITHUB_API_TOKEN GIST_NAME")
        exit(1)

    github_gist_api = "https://api.github.com/gists"
    api_token = sys.argv[1]
    gist_name = sys.argv[2]
    git = Git(github_gist_api, api_token)

    # gistId = git.create_gist(gist_name)
    git.get_and_set_gist_id(gist_name)

    content = "content\ntext\ntest"
    git.update_gist("new", content)
