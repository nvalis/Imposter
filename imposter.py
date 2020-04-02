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

    def spacescience_human_lookup(self, note_id):
        r = self.session.get(
            "https://spacescience.tech/check.php", params={"id": note_id}
        )
        j = json.loads(r.text)
        results = [res["result"] for res in list(j.values())[:-1]]
        return results.count("LOSE") > 0

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
        j = json.loads(r.text)
        return j["result"] == "WIN"

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

    def get_results(self):
        r = self.session.get("https://gremlins-api.reddit.com/results")
        soup = BeautifulSoup(r.content, "lxml")
        stats = " ".join(
            [
                s["aria-label"]
                for s in soup.find("gremlin-meta").find_all(
                    "span", {"aria-label": not None}
                )
            ]
        )
        return stats


def main():
    reddit_username = input("Username: ")
    reddit_password = getpass.getpass("Password: ")

    imposter = Imposter()
    imposter.login(reddit_username, reddit_password)

    for i in range(100):
        if i % 10 == 0:
            print(imposter.get_results())
        imposter.get_notes()

        spacescience = [
            imposter.spacescience_human_lookup(n) for n in imposter.current_notes
        ]
        possible_imposters = [i for i, x in enumerate(spacescience) if not x]

        import random

        if len(possible_imposters) > 1:  # choose random one
            choice = random.choice(possible_imposters)
        elif len(possible_imposters) == 0:  # all are human?!
            print("This should not happen...")
        else:  # choose the only option
            choice = possible_imposters[0]

        win = imposter.submit_guess(list(imposter.current_notes.keys())[choice])
        print(len(possible_imposters), win)


if __name__ == "__main__":
    main()
