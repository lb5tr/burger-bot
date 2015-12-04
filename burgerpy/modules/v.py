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

    def on_until(self, chan, method, prop, body):
        d = json.loads(body)
        now = d["timestamp"]
        departs_at = 1449705600

        delta = str(timedelta(seconds=departs_at-now))
        self.send(d["source"], d["channel"], "%s until lb5tr leaves" % delta)


if __name__ == "__main__":
    c = Config()
    v = VModule(config=c)
    v.listen('burger.command.v', v.on_v)
    v.listen('burger.command.3d', v.on_3d)
    v.listen('burger.command.until', v.on_until)
    v.run()
