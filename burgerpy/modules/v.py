from burgerpy.common import Module, Config

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
                                  json.dumps({"channel": origin,
                                              "content": data["from"]}))
            return

        self.send(origin, data["content"])
        for c in data["content"][1:]:
            if c.isspace():
                self.send(origin, u'\u2000')
            else:
                self.send(origin, c)


if __name__ == "__main__":
    c = Config()
    v = VModule(config=c)
    v.listen('burger.command.v', v.on_v)
    v.run()
