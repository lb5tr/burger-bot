import pika

class RabbitMQ(object):
    def __init__(self, host, port):
        params = pika.ConnectionParameters(host=host, port=port)
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()
        self.queues = {}

    def run(self):
        self.channel.start_consuming()

    def listen(self, key, callback, name):
        queue_name = "%s.%s" % (name, key)
        queue = self.channel.queue_declare(queue=queue_name, exclusive=True)
        self.queues[queue_name] = queue
        self.channel.queue_bind(exchange='bus',
                                queue=queue_name,
                                routing_key=key)

        self.channel.basic_consume(callback,
                                   queue=queue_name,
                                   no_ack=True)

    def send_result(self, exchange, routing_key, msg):
        self.channel.basic_publish(
            exchange='bus',
            routing_key='burger.outbound.send',
            body=msg)


