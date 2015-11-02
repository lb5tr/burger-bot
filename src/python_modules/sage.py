import simplejson as json
from python_common import Module


class SageModule(Module):
    def compose_fail_to_kick(self, user):
        return {
            "command": "msg",
            "user": user,
            "message": "sage who?"
        }

    def compose_kick(self, user, channel):
        return {
            "command": "kick",
            "channel": channel,
            "user": user,
            "reason": ":^)"
        }

    def on_sage(self, ch, method, properties, body):
        data = json.loads(body)
        words = data["content"].split()

        msg = None
        if not words:
            msg = self.compose_fail_to_kick(data["channel"])
        else:
            msg = self.compose_kick(words[0], data["channel"])

        self.send_result(msg)


sm = SageModule()
sm.listen("burger.command.sage", sm.on_sage)
sm.run()
