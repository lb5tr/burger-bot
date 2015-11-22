from burgerpy.common import Module, Config

import simplejson as json


class VModule(Module):
    def on_v(self, chan, method, prop, body):
        data = json.loads(body)
        origin = data["channel"]

        self.send(origin, data["content"])

        for c in data["content"]:
            self.send(origin, c)

if __name__ == "__main__":
    c = Config()
    v = VModule(config=c)
    v.listen('burger.command.v', v.on_v)
    v.run()
