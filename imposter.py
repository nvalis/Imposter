#!/usr/bin/env python
# coding: utf-8

import getpass
import requests
from bs4 import BeautifulSoup


def login(session, reddit_username, reddit_password):
	r = session.get("https://www.reddit.com/login/")
	soup = BeautifulSoup(r.content, "lxml")
	csrf_token = soup.find("input", {"name":"csrf_token"})["value"]
	data = {
	    "csrf_token": csrf_token,
	    "otp": "",
	    "password": reddit_password,
	    "dest": "https://www.reddit.com",
	    "username": reddit_username
	}
	r = session.post("https://www.reddit.com/login", data=data)


def get_notes(session):
    r = session.get("https://gremlins-api.reddit.com/room")
    soup = BeautifulSoup(r.content, "lxml")
    return {n['id']:n.text.replace('\n', '').strip() for n in soup.find_all("gremlin-note")}


def main():
	reddit_username = input("Username: ")
	reddit_password = getpass.getpass("Password: ")
	headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0'}

	session = requests.Session()
	session.headers.update(headers)

	login(session, reddit_username, reddit_password)
	for i, n in get_notes(session).items():
	    print(f"{i}: {n}")

if __name__ == '__main__':
	main()