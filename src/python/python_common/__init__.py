import pika
import simplejson as json

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
