from hashlib import sha1

import simplejson as json
from burgerpy.common import Module, Config


class PickModule(Module):
    def on_pick(self, channel, method, props, body):
            data = json.loads(body)
            words = data["content"].split()
            origin = data["channel"]

            if not words:
                return

            result = self.pick(words)
            msg = self.compose_msg(origin, "%s: %s" % (data["from"], result))
            return self.send_result(data["source"], msg)

    def pick(self, words):
        r = sorted(map(lambda word: (sha1(word).hexdigest(), word), words))
        r = map(lambda t: t[1], r)
        return ' < '.join(r)


if __name__ == "__main__":
    config = Config()
    pm = PickModule(config)
    pm.listen("burger.command.pick", pm.on_pick)
    pm.run()
