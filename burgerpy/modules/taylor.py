import itertools
import random
import simplejson as json

from requests import get

from burgerpy.common import Module, Config


class TaylorQuoteFinder(object):
    API_URL = 'http://lyrics.wikia.com/api.php?action=lyrics&artist=Taylor%20Swift&fmt=realjson'  # noqa
    WHITELIST = ["1989", "Red"]

    def roll(self):
        albums = get(self.API_URL).json()['albums']
        songs = [v['songs'] for v in albums if v['album'] in self.WHITELIST]
        songs = list(itertools.chain(*songs))
        song = random.choice(songs)

        lyrics = get(self.API_URL + "&song=" + song).json()['lyrics']
        lines = [l for l in lyrics.split('\n') if l.strip()]
        return random.choice(lines)


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
