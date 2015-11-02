from hashlib import sha1

import simplejson as json
from python_common import Module


class PickModule(Module):
    def on_pick(self, channel, method, props, body):
            data = json.loads(body)
            words = data["content"].split()
            origin = data["channel"]

            if not words:
                return

            result = self.pick(words)
            msg = self.compose_msg(origin, "%s: %s" % (data["from"], result))
            self.send_result(msg)

    def pick(self, words):
        r = sorted(map(lambda word: (sha1(word).hexdigest(), word), words))
        r = map(lambda t: t[1], r)
        return ' < '.join(r)


pm = PickModule()
pm.listen("burger.command.pick", pm.on_pick)
pm.run()
