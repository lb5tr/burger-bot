import simplejson as json
from burgerpy.common import Module, Config


class SageModule(Module):
    def compose_fail_to_kick(self, user):
        return {
            "command": "msg",
            "user": user,
            "message": "sage who?"
        }

    def compose_kick(self, user, channel, reason):
        return {
            "command": "kick",
            "channel": channel,
            "user": user,
            "reason": reason
        }

    def on_sage(self, ch, method, properties, body):
        data = json.loads(body)
        words = data["content"].split()
        reason = ' '.join(words[1:])

        msg = None
        if not words:
            msg = self.compose_fail_to_kick(data["channel"])
        else:
            msg = self.compose_kick(words[0], data["channel"], reason)

        self.send_result(data["source"], msg)


if __name__ == "__main__":
    config = Config()
    sm = SageModule(config)
    sm.listen("burger.command.sage", sm.on_sage)
    sm.run()
