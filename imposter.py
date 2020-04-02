#!/usr/bin/env python
# coding: utf-8

import getpass
import requests
import json
from bs4 import BeautifulSoup


class Imposter:
    def __init__(self, headers=None, proxies=None):
        self.session = requests.Session()
        if headers is None:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0"
            }
        self.session.headers.update(headers)
        if proxies is not None:
            self.session.proxies.update(proxies)

    def login(self, username, password):
        r = self.session.get("https://www.reddit.com/login/")
        soup = BeautifulSoup(r.content, "lxml")
        csrf_token = soup.find("input", {"name": "csrf_token"})["value"]
        data = {
            "csrf_token": csrf_token,
            "otp": "",
            "password": password,
            "dest": "https://www.reddit.com",
            "username": username,
        }
        r = self.session.post("https://www.reddit.com/login", data=data)

    def get_csrf_token(self, soup):
        return soup.find("gremlin-app")["csrf"]

    def get_notes(self):
        r = self.session.get("https://gremlins-api.reddit.com/room")
        soup = BeautifulSoup(r.content, "lxml")
        self.current_notes = {
            n["id"]: n.text.replace("\n", "").strip()
            for n in soup.find_all("gremlin-note")
        }
        self.current_csrf_token = self.get_csrf_token(soup)

    def submit_guess(self, note_id):
        data = {
            "undefined": "undefined",
            "note_id": note_id,
            "csrf_token": self.current_csrf_token,
        }
        r = self.session.post("https://gremlins-api.reddit.com/submit_guess", data=data)
        return r

    def create_note(self, note):
        r = self.session.get("https://gremlins-api.reddit.com/create_note")
        csrft = self.get_csrf_token(BeautifulSoup(r.content, "lxml"))
        data = {"note": note, "csrf_token": csrft}
        r = self.session.post("https://gremlins-api.reddit.com/create_note", data=data)
        if "doctype html" in r.text:
            soup = BeautifulSoup(r.content, "lxml")
            print(soup.find("body").text)
            # probably submitted too soon
            # TODO: proper error handling
        else:
            ans = json.loads(r.content)
            if ans["success"]:
                return ans["note_id"]
            else:
                print(ans)


def main():
    reddit_username = input("Username: ")
    reddit_password = getpass.getpass("Password: ")

    imposter = Imposter()
    imposter.login(reddit_username, reddit_password)

    # get notes to choose from and select a random one
    imposter.get_notes()
    import random
    rand_note_id = random.choice(list(imposter.current_notes.keys()))
    r = imposter.submit_guess(rand_note_id)

    # update my own note and get its note_id
    note_id = imposter.create_note("six times seven plus five equals fourtyseven")
    print(note_id)


if __name__ == "__main__":
    main()
