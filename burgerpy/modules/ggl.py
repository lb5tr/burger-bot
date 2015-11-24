from burgerpy.common import Module, Config
from burgerpy.common.utils import strip_tags
from requests import get
from urllib import unquote
import simplejson as json


class GoogleSearch(object):
    url = 'http://ajax.googleapis.com/ajax/services/search/web'

    def search(self, query):
        return get(self.url, params={"v": "1.0", "q": query})

    def format_result(self, result):
        msg = "%s: %s - %s" % (
            result["titleNoFormatting"],
            unquote(result["url"]),
            unquote(strip_tags(result["content"])))
        return msg

    def get_results(self, response):
        results = response.json()["responseData"]["results"]
        return results

    def lucky_guess(self, query):
        r = self.search(query)
        r = self.get_results(r)

        if len(r) == 0:
            return "No results found for query %s" % query

        return self.format_result(r[0])


class GoogleModule(Module):
    def __init__(self, search_module, config):
        super(GoogleModule, self).__init__(config)
        self.search = search_module

    def on_google(self, ch, method, properties, body):
        data = json.loads(body)
        origin = data["channel"]
        query = data["content"]
        search_results = self.search.lucky_guess(query)

        msg = self.compose_msg(origin, search_results)
        self.send_result(msg)


if __name__ == "__main__":
    config = Config()
    sm = GoogleSearch()
    gm = GoogleModule(sm, config)
    gm.listen('burger.command.g', gm.on_google)
    gm.run()
