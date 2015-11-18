import os
import simplejson as json

from git import Repo
from amqp import RabbitMQ


class Config(object):
    def __init__(self):
        base_dir = os.getenv('BURGER_DIR') or os.path.dirname(os.path.realpath(__file__)) + '/../../envs/'
        env = os.getenv('BURGER_ENV') or 'DEV'
        d = self._load_config(base_dir, env)

        for a, b in d.items():
            if isinstance(b, (list, tuple)):
                setattr(self, a, [obj(x) if isinstance(x, dict) else x for x in b])
            else:
                setattr(self, a, obj(b) if isinstance(b, dict) else b)

    def _load_config(self, base_dir, env):
        with open('%s%s.json' % (base_dir, env)) as f:
            data = f.read()
            return json.loads(data)


class Module(object):
    def __init__(self, config, amqp_iface=None):
        if amqp_iface is None:
            amqp_iface = RabbitMQ(config.amqp_server, config.amqp_port)

        self.amqp = amqp_iface
        self.app_config = config
        self.name = self.__class__.__name__
        self.version = self._get_version()
        self.listen("burger.command.version", self._on_version)

    def _on_version(self, chan, method, properties, body):
        data = json.loads(body)
        origin = data["channel"]
        self.send_result(self.compose_msg(origin,
                                          "%s revision is %s" % (
                                              self.name,
                                              self.version)))

    def listen(self, key, callback):
        self.amqp.listen(key, callback, self.name, 'bus')

    def run(self):
        self.amqp.run()

    def send_result(self, msg):
        return self.amqp.send_result('bus', 'burger.outbound.send', json.dumps(msg))

    def compose_msg(self, user, msg):
        return {
            "command": "msg",
            "user": user,
            "message": msg
        }

    def _get_version(self):
        repo = Repo(self.app_config.base_dir)
        return repo.head.commit.hexsha
