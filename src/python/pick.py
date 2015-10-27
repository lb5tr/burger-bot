from hashlib import sha1

import pika
import simplejson as json
from python_common import Module


class PickModule(Module):
    def on_message(self, channel, method, props, body):
            data = json.loads(body)
            content = data["content"]
            words = data["content"].split()

            if not words:
                return

            result = self.pick(words)
            msg = self.compose_response(data, result)
            self.send_result(msg)

    def compose_response(self, msg, result):
        return {
            "command": "msg",
            "message": "%s: %s" % (msg["from"], result),
            "from": msg["from"],
            "user": msg["channel"]
        }

    def pick(self, words):
        r = sorted(map(lambda word: (sha1(word).hexdigest(), word), words))
        r = map(lambda t: t[1], r)
        return ' < '.join(r)


pm = PickModule("pick", ["burger.command.pick"])
pm.run()
