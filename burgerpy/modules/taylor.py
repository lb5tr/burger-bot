from burgerpy.common import Module, Config
from requests import get
import simplejson as json
import random


class TaylorQuoteFinder(object):
    apiURL = 'http://lyrics.wikia.com/api.php?action=lyrics&artist=Taylor%20Swift&fmt=realjson'

    whiteList = ["1989", "Red"]

    def roll(self):
        response = get(self.apiURL).json()
        songs = map(lambda x: x["songs"] if x["album"] in self.whiteList else None, response["albums"])
        songs = filter(lambda x: True if x is not None else False, songs)

        songs = reduce(list.__add__, songs)

        song = random.choice(songs)

        songLyrics = get(self.apiURL + "&song=" + song).json()["lyrics"]
        lyricsLines = filter(lambda x: True if x is not "" else False, songLyrics.split("\n"))
        del lyricsLines[-1]

        return random.choice(lyricsLines)


class TaylorModule(Module):
    def __init__(self, search_module, config):
        super(TaylorModule, self).__init__(config)
        self.search = search_module

    def on_taylor(self, ch, method, properties, body):
        data = json.loads(body)
        origin = data["channel"]
        search_results = self.search.roll()

        msg = self.compose_msg(origin, search_results)
        self.send_result(data["source"], msg)


if __name__ == "__main__":
    config = Config()
    qf = TaylorQuoteFinder()
    tm = TaylorModule(qf, config)
    tm.listen('burger.command.taylor', tm.on_taylor)
    tm.run()
