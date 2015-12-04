from burgerpy.common import Module, Config

import simplejson as json

class DispatcherModule(Module):
    def _get_nickname(self, user_line):
        return user_line.split('!', 1)[0]

    def _is_command(self, word):
        return word[0] == self.app_config.command_character

    def _get_command(self, msg):
        if msg == "":
            raise LookupError('empty message')

        first_word = msg.split(' ')[0]
        return first_word[1:]

    def _get_command_params(self, msg):
        return ' '.join(msg.split(' ')[1:])

    def on_privmsg(self, channel, method, props, body):
        data = json.loads(body)
        nick = self._get_nickname(data["from"])
        content = data["content"]

        if not self._is_command(content):
            return

        data["content"] = self._get_command_params(content)
        command = self._get_command(content)
        print command
        print data
        self.amqp.send_result('bus',
                              "burger.command.%s" % command,
                              json.dumps(data))

if __name__ == "__main__":
    config = Config()
    d = DispatcherModule(config)
    d.listen('burger.privmsg', d.on_privmsg)
    d.run()
