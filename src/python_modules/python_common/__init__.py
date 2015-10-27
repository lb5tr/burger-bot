import pika
import os
import simplejson as json


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
    def __init__(self, name, routing_keys):
        params = pika.ConnectionParameters(host='localhost')
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()
        self.name = name
        self.queue = self.channel.queue_declare(queue=self.name, exclusive=True)

        for key in routing_keys:
            self.channel.queue_bind(exchange='bus',
                                    queue=self.name,
                                    routing_key=key)

        self.channel.basic_consume(self.on_message,
                                   queue=self.name,
                                   no_ack=True)

    def run(self):
        self.channel.start_consuming()

    def send_result(self, msg):
        self.channel.basic_publish(
            exchange='bus',
            routing_key='burger.outbound.send',
            body=json.dumps(msg))

    def on_message(self, channel, method, props, body):
        raise NotImplemented()

    def compose_msg(self, user, msg):
        return {
            "command": "msg",
            "user": user,
            "message": msg
        }
