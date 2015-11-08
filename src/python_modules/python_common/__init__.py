import pika
import os
import simplejson as json
from git import Repo

class Config(object):
    def __init__(self):
        base_dir = os.getenv('BURGER_DIR') or  '../envs/'
        env = os.getenv('BURGER_ENV') or 'DEV'
        d = self._load_config(base_dir, env)

        for a, b in d.items():
            if isinstance(b, (list, tuple)):
               setattr(self, a, [obj(x) if isinstance(x, dict) else x for x in b])
            else:
               setattr(self, a, obj(b) if isinstance(b, dict) else b)

    def _load_config(self, base_dir, env):
        with open('%s%s.json'% (base_dir, env)) as f:
            data = f.read()
            return json.loads(data)


class Module(object):
    def __init__(self, config):
        params = pika.ConnectionParameters(host='localhost')
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()
        self.name = self.__class__.__name__
        self.queues = {}
        self.app_config = config
        self.version = self._get_version()
        self._get_version()
        self.listen("burger.command.version", self._on_version)

    def _on_version(self, chan, method, properties, body):
        data = json.loads(body)
        origin = data["channel"]
        self.send_result(self.compose_msg(origin,
                                          "%s revision is %s" % (
                                              self.name,
                                              self.version)))

    def _get_version(self):
        repo = Repo(self.app_config.base_dir)
        self.version = repo.head.commit.hexsha

    def listen(self, key, callback):
        queue_name = "%s.%s" % (self.name, key)
        queue = self.channel.queue_declare(queue=queue_name, exclusive=True)
        self.queues[queue_name] = queue
        self.channel.queue_bind(exchange='bus',
                                queue=queue_name,
                                routing_key=key)

        self.channel.basic_consume(callback,
                                   queue=queue_name,
                                   no_ack=True)

    def run(self):
        self.channel.start_consuming()

    def send_result(self, msg):
        self.channel.basic_publish(
            exchange='bus',
            routing_key='burger.outbound.send',
            body=json.dumps(msg))

    def compose_msg(self, user, msg):
        return {
            "command": "msg",
            "user": user,
            "message": msg
        }
