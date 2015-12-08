# -*- coding: utf-8 -*-
from burgerpy.common import Module, Config

import simplejson as json
import re
from lxml.html import fromstring
import requests


class URLSModule(Module):
    regex = '/(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?/'

    def get_title(self, url):
        r = requests.get(url, verify=False)
        root = fromstring(r.content)
        title = root.findtext(".//title")
        if title is None:
            raise ValueError
        else:
            return title.strip()

    def format_title(self, title):
        title = title.encode('utf-8')
        return"↳ %s" % title

    def title(self, url):
        return self.format_title(self.get_title(url))

    def on_privmsg(self, chan, method, prop, body):
        data = json.loads(body)
        content = data["content"]
        origin = data["channel"]
        matches = re.findall(r'(https?://\S+)', content)

        try:
            map(lambda url: self.send(data["source"], origin, self.title(url)), matches)
        except ValueError:
            return

if __name__ == "__main__":
    c = Config()
    u = URLSModule(config=c)
    u.listen('burger.privmsg', u.on_privmsg)
    u.run()
