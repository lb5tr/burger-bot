from burgerpy.common import Module, Config
from burgerpy.common.cube import Renderer
from datetime import timedelta
import simplejson as json


class VModule(Module):
    def on_v(self, chan, method, prop, body):
        data = json.loads(body)
        origin = data["channel"]
        if data["from"] == self.app_config.irc_nick:
            return

        if len(data["content"]) > 15:
            self.amqp.send_result('bus',
                                  'burger.command.sage',
                                  json.dumps({
                                      "source" : "burger.irc.out",
                                      "channel": origin,
                                      "content": data["from"]}))
            return

        self.send(data["source"], origin, " ".join(data["content"]))
        for c in data["content"][1:]:
            if c.isspace():
                self.send(data["source"], origin, u'\u2000')
            else:
                self.send(data["source"], origin, c)

    def on_3d(self, chan, method, prop, body):
        d = json.loads(body)

        if len(d["content"]) == 0:
            return

        r = Renderer()

        for line in r.get(d["content"]):
            self.send(d["source"], d["channel"], line)

    def deadline(self, departs_at, description):
        """Returns a handler for a deadline-check command."""
        def _handler(chan, method, prop, body):
            d = json.loads(body)
            now = d['timestamp']
            diff = departs_at - now
            if diff > 0:
                delta = str(timedelta(seconds=departs_at-now))
                self.send(d['source'], d['channel'], description % delta)
        return _handler


if __name__ == "__main__":
    c = Config()
    v = VModule(config=c)
    v.listen('burger.command.v', v.on_v)
    v.listen('burger.command.3d', v.on_3d)

    v.listen('burger.command.until', v.deadline(1449725100, "%s until lb5tr leaves"))
    v.listen('burger.command.nyc', v.deadline(1450942200, "%s until TXL-MUC for NYC leaves"))
    v.listen('burger.command.q3k', v.deadline(1454277000, "%s until q3k is all ogre"))
    v.run()
